import logging
from datetime import datetime

from models import User, Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse, Scenario, ScenarioStep
from services.constants import Replies, MenuButtons
from services.repostiories import Repository
from services.utils import create_reply_keyboard_response, create_message_response
from services.utils import create_calendar_response

logger = logging.getLogger(__name__)


class WorkTimeReportScenario:
    name = 'work_time_report'

    def __init__(self, repository: Repository):
        self.repository = repository
        self.step_dispatcher = {
            1: self.step_1,
            2: self.step_2,
            3: self.step_3,
            4: self.step_4,
            5: self.step_5,
        }

    async def step_5(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 5
        await self._add_step(step_number, user, scenario)
        return await create_reply_keyboard_response(
            messages=['Step 5'],
            buttons=[],
        )

    async def step_4(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 4
        await self._add_step(step_number, user, scenario)
        timings = [
            ['00:15', '00:30', '00:45', '01:00'],
            ['01:15', '01:30', '01:45', '02:00'],
            ['02:15', '02:30', '02:45', '03:00'],
            ['03:15', '03:30', '03:45', '04:00']
        ]
        if message is not None:
            try:
                hours, minutes = message.split(':')
                if int(hours) > 23 or int(minutes) > 59:
                    raise ValueError
                return await self._fix_and_next(step_number, message, user, scenario)
            except ValueError:
                return await create_reply_keyboard_response(
                    messages=[Replies.WRONG_TIME_FORMAT, Replies.ENTER_TIME, Replies.CHOOSE_TIME],
                    buttons=timings,
                )
        return await create_reply_keyboard_response(
            messages=[Replies.ENTER_TIME, Replies.CHOOSE_TIME],
            buttons=timings,
        )

    async def step_3(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 3
        await self._add_step(step_number, user, scenario)
        clients = await self.repository.clients.get_clients(is_completed=False)
        client_list = [[client.name] for client in clients]
        if message is not None:
            if message not in [client.name for client in clients]:
                return await create_reply_keyboard_response(
                    messages=[Replies.WRONG_CLIENT, Replies.CHOOSE_CLIENT],
                    buttons=client_list,
                )
            return await self._fix_and_next(step_number, message, user, scenario)
        return await create_reply_keyboard_response(
            messages=[Replies.CHOOSE_CLIENT],
            buttons=client_list,
        )

    async def step_2(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 2
        await self._add_step(step_number, user, scenario)
        work_types = await self.repository.work_types.get_work_types()
        work_list = [[work_type.name] for work_type in work_types]
        if message is not None:
            if message not in [work_type.name for work_type in work_types]:
                return await create_reply_keyboard_response(
                    messages=[Replies.WRONG_WORK_TYPE, Replies.CHOOSE_WORK_TYPE],
                    buttons=work_list,
                )
            return await self._fix_and_next(step_number, message, user, scenario)
        return await create_reply_keyboard_response(
            messages=[Replies.CHOOSE_WORK_TYPE],
            buttons=work_list,
        )

    async def step_1(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 1
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
                )
        return await create_calendar_response(
            messages=[Replies.ENTER_DATE, Replies.CHOOSE_DATE],
            year=datetime.now().year,
            month=datetime.now().month,
        )

    async def _add_step(self, step: int, user: User, scenario: Scenario) -> Scenario:
        for _step in scenario.steps:
            if _step.number == step:
                return scenario
        scenario.steps.append(ScenarioStep(number=step))
        await self.repository.scenarios.upsert_user_scenario(user, scenario)
        return scenario

    async def _fix_and_next(self, step: int, result: str, user: User, scenario: Scenario) -> Response:
        for _step in scenario.steps:
            if _step.number == step:
                _step.result = result
                break
        scenario.current_step = step + 1
        await self.repository.scenarios.upsert_user_scenario(user, scenario)
        return await self.step_dispatcher[scenario.current_step](user, scenario)

    async def finish(self, user: User) -> Response:
        pass

    async def start(self, user: User) -> Response:
        _user_scenario = Scenario(
            name=self.name,
            current_step=1,
            steps=[ScenarioStep(number=1)],
        )
        await self.repository.scenarios.upsert_user_scenario(user, _user_scenario)
        return await self.step_1(user, _user_scenario)

    async def prologue(
        self,
        message: str,
        user: User,
        user_scenario: Scenario | None = None,
    ) -> Response:
        if user_scenario is None:
            return await self.start(user)

        return await self.step_dispatcher[user_scenario.current_step](user, user_scenario, message)
