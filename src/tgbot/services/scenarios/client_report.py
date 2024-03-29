import logging
from datetime import datetime
from enum import StrEnum

from aiogram.filters.callback_data import CallbackData

from models import User, Scenario, ScenarioStep
from models import Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse, FinalResponse
from services.constants import Replies, MenuButtons, Notifications
from services.notifier import AbstractNotifier
from services.repostiories import Repository
from services.utils import create_calendar_response, create_reply_keyboard_response, create_message_response, create_inline_keyboard_response

logger = logging.getLogger(__name__)


class ClientReportAct(StrEnum):
    NEXT_REPORT = 'next'
    PREV_REPORT = 'prev'
    REMOVE_REPORT = 'remove'
    IGNORE = 'ignore'
    OUT = 'out'


class ClientReportActCallback(CallbackData, prefix='act_report'):
    act: ClientReportAct
    report_id: int | None = None  # row_id in model


class ClientReportScenario:
    name = 'client_report'
    report_from_date_step = 1
    report_to_date_step = 2
    report_client_step = 3
    report_user_step = 4
    act_report_step = 5
    
    def __init__(self, repository: Repository, notifier: AbstractNotifier):
        self.repository = repository
        self.notifier = notifier
        self.step_dispatcher = {
            self.report_from_date_step: self.enter_from_date,
            self.report_to_date_step: self.enter_to_date,
            self.report_client_step: self.choose_client,
            self.report_user_step: self.choose_user,
            self.act_report_step: self.act_report,
        }

    async def act_report(
        self,
        user: User,
        scenario: Scenario,
        message: str | None = None,
    ) -> Response:
        step_number = self.act_report_step
        await self._add_step(step_number, user, scenario)

        report_from_date = scenario.steps[self.report_from_date_step - 1].result
        report_to_date = scenario.steps[self.report_to_date_step - 1].result
        report_client = scenario.steps[self.report_client_step - 1].result
        report_user = scenario.steps[self.report_user_step - 1].result

        if message is None:
            await self.notifier.notify(Replies.LOADING, user)

        reports = await self.repository.work_time_reports.get_reports(
            user=user,
            report_from_date=report_from_date,
            report_to_date=report_to_date,
            client=report_client,
            user_id=report_user,
        )
        stats = await self.repository.work_time_reports.get_stats(
            user=user,
            report_from_date=report_from_date,
            report_to_date=report_to_date,
            client=report_client,
            user_id=report_user,
        )

        edit_keyboard = False
        delete_keyboard = False
        delete_keyboard_and_continue = False
        current_report = None
        current_report_index = None
        next_button = False
        prev_button = False
        pre_inline_msg = None

        if message is not None:
            try:
                callback_data = ClientReportActCallback.unpack(message)
            except (ValueError, TypeError) as exc:
                logger.exception(exc)
                await self.notifier.notify(Notifications.CALLBACK_DATA_ERROR, user)
                await self.notifier.notify(Notifications.RETRY_OR_CALL_ADMIN, user)
            else:
                index_offset = 0
                if callback_data.act == ClientReportAct.NEXT_REPORT:
                    edit_keyboard = True
                    index_offset = 1
                elif callback_data.act == ClientReportAct.PREV_REPORT:
                    edit_keyboard = True
                    index_offset = -1
                elif callback_data.act == ClientReportAct.REMOVE_REPORT:
                    remove_result = await self.repository.work_time_reports.delete_report(
                        callback_data.report_id
                    )
                    if not remove_result:
                        await self.notifier.notify(Notifications.RETRY_OR_CALL_ADMIN, user)
                        edit_keyboard = True
                        index_offset = 0
                    else:
                        await self.repository.work_time_reports.remove_reports_from_cache(user)
                        reports = await self.repository.work_time_reports.get_reports(
                            user=user,
                            report_from_date=report_from_date,
                            report_to_date=report_to_date,
                            client=report_client,
                            user_id=report_user,
                        )
                        stats = await self.repository.work_time_reports.get_stats(
                            user=user,
                            report_from_date=report_from_date,
                            report_to_date=report_to_date,
                            client=report_client,
                            user_id=report_user,
                        )
                        await self.notifier.notify(Replies.REPORT_DELETED, user)
                        pre_inline_msg = stats.get_msg()
                        delete_keyboard_and_continue = True
                        edit_keyboard = False
                        current_report = reports[0] if reports else None
                        current_report_index = 1
                        next_button = len(reports) > 1 and current_report is not None
                elif callback_data.act == ClientReportAct.OUT:
                    return await self.finish(user, scenario)
                elif callback_data.act == ClientReportAct.IGNORE:
                    pass

                for i, report in enumerate(reports):
                    if report.row_id == callback_data.report_id:
                        reports_length = len(reports)
                        next_button = i + index_offset < reports_length - 1
                        prev_button = i + index_offset > 0
                        try:
                            current_report = reports[i + index_offset]
                            current_report_index = i + index_offset + 1
                        except IndexError:
                            logger.error(f'IndexError: {i + index_offset} for reports pagination')
                            current_report = reports[i]
                            current_report_index = i + 1
                        break
        else:
            pre_inline_msg = stats.get_msg()
            current_report = reports[0] if reports else None
            next_button = len(reports) > 1 and current_report is not None
            current_report_index = 1

        if current_report is not None:
            client_btn = (
                current_report.client,
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            work_type_btn = (
                current_report.work_type,
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            hours_btn = (
                f'{current_report.hours} ч',
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            comment_btn = (
                f'Комментарий: {current_report.comment}',
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            buttons = [
                [client_btn],
                [work_type_btn],
                [hours_btn],
                [comment_btn],
            ]
            if user.admin:
                staff_btn = (
                    f'Сотрудник: {current_report.user_fullname}',
                    ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
                )
                buttons.append([staff_btn])
            paginate_btns = []
            if prev_button:
                prev_report_btn = (
                    '<< Пред.',
                    ClientReportActCallback(
                        act=ClientReportAct.PREV_REPORT,
                        report_id=current_report.row_id,
                    ).pack(),
                )
            else:
                prev_report_btn = (
                    ' ',
                    ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
                )
            paginate_btns.append(prev_report_btn)
            page_number_btn = (
                f'{current_report_index}/{len(reports)}',
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            paginate_btns.append(page_number_btn)
            if next_button:
                next_report_btn = (
                    'След. >>',
                    ClientReportActCallback(
                        act=ClientReportAct.NEXT_REPORT,
                        report_id=current_report.row_id,
                    ).pack(),
                )
            else:
                next_report_btn = (
                    ' ',
                    ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
                )
            paginate_btns.append(next_report_btn)
            delete_btn = (
                'Удалить',
                ClientReportActCallback(
                    act=ClientReportAct.REMOVE_REPORT,
                    report_id=current_report.row_id,
                ).pack(),
            )
            out_btn = (
                Replies.BACK_TO_MENU,
                ClientReportActCallback(act=ClientReportAct.OUT).pack(),
            )
            buttons.extend([
                paginate_btns,
                [delete_btn],
                [out_btn],
            ])
        else:
            no_reports_btn = (
                Replies.NO_REPORTS,
                ClientReportActCallback(act=ClientReportAct.IGNORE).pack(),
            )
            out_btn = (
                Replies.BACK_TO_MENU,
                ClientReportActCallback(act=ClientReportAct.OUT).pack(),
            )
            buttons = [
                [no_reports_btn],
                [out_btn],
            ]

        messages = [pre_inline_msg] if pre_inline_msg else []

        return await create_inline_keyboard_response(
            messages=messages,
            buttons=buttons,
            delete_reply_keyboard=delete_keyboard,
            edit_reply_keyboard=edit_keyboard,
            delete_reply_keyboard_and_continue=delete_keyboard_and_continue,
        )

    async def choose_user(
        self,
        user: User,
        scenario: Scenario,
        message: str | None = None,
    ) -> Response:
        step_number = self.report_user_step
        await self._add_step(step_number, user, scenario)
        if not user.admin:
            return await self._fix_and_next(step_number, user.id, user, scenario)

        users = await self.repository.users.get_users()
        users_buttons = [[user.fullname] for user in users]
        users_buttons.append([Replies.SKIP])

        if message is not None:
            if message == Replies.SKIP:
                return await self._fix_and_next(step_number, user.id, user, scenario)
            right_answers = {user.fullname: user.id for user in users}
            user_id = right_answers.get(message)
            if user_id is None:
                return await create_reply_keyboard_response(
                    messages=[Replies.WRONG_USER, Replies.CHOOSE_USER],
                    buttons=users_buttons,
                    resize_keyboard=True,
                )
            return await self._fix_and_next(step_number, user_id, user, scenario)

        return await create_reply_keyboard_response(
            messages=[Replies.CHOOSE_USER],
            buttons=users_buttons,
            resize_keyboard=True,

        )

    async def choose_client(
        self,
        user: User,
        scenario: Scenario,
        message: str | None = None,
    ) -> Response:
        step_number = self.report_client_step
        await self._add_step(step_number, user, scenario)
        clients = await self.repository.clients.get_clients(is_completed=False)
        client_list = [[client.name] for client in clients]
        if scenario.steps[self.report_from_date_step - 1].result is not None:
            client_list.append([Replies.SKIP])
        if message is not None:
            right_answers = [client.name for client in clients]
            right_answers.extend([Replies.SKIP])
            if message not in right_answers:
                return await create_reply_keyboard_response(
                    messages=[Replies.WRONG_CLIENT, Replies.CHOOSE_CLIENT],
                    buttons=client_list,
                    resize_keyboard=True,
                )
            if message == Replies.SKIP:
                message = None
            return await self._fix_and_next(step_number, message, user, scenario)
        return await create_reply_keyboard_response(
            messages=[Replies.CHOOSE_CLIENT],
            buttons=client_list,
            resize_keyboard=True,
        )

    async def enter_to_date(
        self,
        user: User,
        scenario: Scenario,
        message: str | None = None,
    ) -> Response:
        step_number = self.report_to_date_step
        if len(scenario.steps) < step_number and scenario.steps[-1].result is None:
            await self._add_step(step_number, user, scenario)
            return await self._fix_and_next(step_number, message, user, scenario)
        return await self.enter_date(step_number, user, scenario, message)

    async def enter_from_date(
        self,
        user: User,
        scenario: Scenario,
        message: str | None = None,
    ) -> Response:
        step_number = self.report_from_date_step
        if message == Replies.SKIP:
            return await self._fix_and_next(step_number, None, user, scenario)
        return await self.enter_date(step_number, user, scenario, message, skip_calendar=True)

    async def enter_date(
        self,
        step_number: int,
        user: User,
        scenario: Scenario,
        message: str | None = None,
        skip_calendar: bool = False,
    ) -> Response:
        await self._add_step(step_number, user, scenario)
        if message is not None:
            try:
                message_date = datetime.strptime(message, '%d.%m.%Y')
                return await self._fix_and_next(step_number, message, user, scenario)
            except ValueError:
                return await create_calendar_response(
                    messages=[Replies.WRONG_DATE_FORMAT, Replies.ENTER_DATE, Replies.CHOOSE_DATE],
                    year=datetime.now().year,
                    month=datetime.now().month,
                    skip_calendar=skip_calendar,
                )
        return await create_calendar_response(
            messages=[Replies.ENTER_DATE, Replies.CHOOSE_DATE],
            year=datetime.now().year,
            month=datetime.now().month,
            skip_calendar=skip_calendar,
        )

    async def finish(self, user: User, scenario: Scenario, *args, **kwargs):
        await self.repository.work_time_reports.delete_scenario_and_reports_from_cache(user)
        return FinalResponse()

    async def start(self, user: User) -> Response:
        _scenario = Scenario(
            name=self.name,
            current_step=1,
            steps=[ScenarioStep(number=1)],
        )
        await self.repository.scenarios.upsert_user_scenario(user, _scenario)
        return await self.step_dispatcher[1](user, _scenario)

    async def prologue(
        self,
        message: str | None,
        user: User,
        user_scenario: Scenario | None = None,
    ) -> Response:
        if user_scenario is None:
            return await self.start(user)
        return await self.step_dispatcher[user_scenario.current_step](user, user_scenario, message)

    async def _add_step(self, step: int, user: User, scenario: Scenario) -> Scenario:
        for _step in scenario.steps:
            if _step.number == step:
                return scenario
        scenario.steps.append(ScenarioStep(number=step))
        await self.repository.scenarios.upsert_user_scenario(user, scenario)
        return scenario

    async def _fix_and_next(
        self,
        step: int,
        result: str | None,
        user: User,
        scenario: Scenario,
    ) -> Response:
        for _step in scenario.steps:
            if _step.number == step:
                _step.result = result
                break
        scenario.current_step = step + 1
        await self.repository.scenarios.upsert_user_scenario(user, scenario)
        return await self.step_dispatcher[scenario.current_step](user, scenario)
