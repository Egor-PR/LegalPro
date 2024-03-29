import logging

from models import User, Response

from .constants import Replies, MenuButtons
from .notifier import AbstractNotifier
from .repostiories import Repository
from .scenarios import ClientReportScenario, WorkTimeReportScenario
from .utils import create_reply_keyboard_response, create_message_response

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, repository: Repository, notifier: AbstractNotifier):
        self.repository = repository
        self.notifier = notifier

    async def logout(self, user: User | None):
        if user is None:
            return await self.start(user)
        await self.repository.work_time_reports.delete_scenario_and_reports_from_cache(user)
        await self.repository.users.delete_user(user.chat_id)
        return await self.execute(user_message=None, user=None, chat_id=user.chat_id)

    async def back(self, user: User | None) -> Response:
        if user is None:
            return await self.start(user)
        scenario = await self.repository.scenarios.get_user_scenario(user)
        if scenario:
            scenario.steps = scenario.steps[:-1]
            if scenario.steps:
                scenario.steps[-1].result = None
                scenario.current_step = scenario.steps[-1].number
            await self.repository.scenarios.upsert_user_scenario(user, scenario)
        return await self.execute(user_message=None, user=user)

    async def reset(self, user: User | None) -> Response:
        if user is None:
            return await self.start(user)
        scenario = await self.repository.scenarios.get_user_scenario(user)
        if scenario:
            scenario.steps = scenario.steps[:1]
            if scenario.steps:
                scenario.steps[0].result = None
                scenario.current_step = scenario.steps[0].number
            await self.repository.scenarios.upsert_user_scenario(user, scenario)

        if scenario.name == WorkTimeReportScenario.name:
            name = MenuButtons.TIME_REPORT
        else:
            name = MenuButtons.CLIENT_REPORT
        await self.notifier.notify(name, user)
        return await self.execute(user_message=None, user=user)

    async def start(self, user: User | None) -> Response:
        if user:
            await self.repository.work_time_reports.delete_scenario_and_reports_from_cache(user)
            return await self.menu(user)
        else:
            return await create_message_response([
                Replies.PLEASE_AUTH, Replies.ENTER_PERSONAL_CODE
            ])

    async def menu(self, user: User) -> Response:
        menu_buttons = [
            [MenuButtons.TIME_REPORT],
            [MenuButtons.CLIENT_REPORT],
        ]
        return await create_reply_keyboard_response(
            messages=[Replies.CHOOSE_MENU],
            buttons=menu_buttons,
            resize_keyboard=True
        )

    async def auth(self, chat_id: int) -> User | None:
        return await self.repository.users.get_user_by_chat_id(chat_id)

    async def authenticate(self, user_code: str | None, chat_id: int | None = None) -> Response:
        if user_code is not None:
            user = await self.repository.users.get_user_by_code(user_code)
            if user is None:
                return await create_message_response([
                    Replies.WRONG_PERSONAL_CODE, Replies.PLEASE_AUTH, Replies.ENTER_PERSONAL_CODE
                ])
            user.chat_id = chat_id
            await self.repository.users.upsert(user)
            await self.notifier.notify(f'Вы авторизовались как {user.fullname}', user)
            return await self.menu(user)
        return await create_message_response([
            Replies.PLEASE_AUTH, Replies.ENTER_PERSONAL_CODE
        ])

    async def execute(
        self,
        user_message: str | None,
        user: User | None,
        chat_id: int | None = None,
    ) -> Response:
        if user is None:
            return await self.authenticate(user_message, chat_id)

        user_scenario = await self.repository.scenarios.get_user_scenario(user)

        response = None
        if user_scenario and user_scenario.name == WorkTimeReportScenario.name:
            response = await WorkTimeReportScenario(self.repository, self.notifier).prologue(
                user_message, user, user_scenario
            )
        elif user_scenario and user_scenario.name == ClientReportScenario.name:
            response = await ClientReportScenario(self.repository, self.notifier).prologue(
                user_message, user, user_scenario
            )

        if response is None:
            if user_message == MenuButtons.TIME_REPORT:
                response = await WorkTimeReportScenario(self.repository, self.notifier).prologue(
                    user_message, user
                )
            elif user_message == MenuButtons.CLIENT_REPORT:
                response = await ClientReportScenario(self.repository, self.notifier).prologue(
                    user_message, user
                )

        if isinstance(response, Response):
            return response

        return await self.menu(user)
