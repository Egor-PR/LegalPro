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
        }

    async def step_2(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 2
        return await create_message_response(['New step 2'])

    async def step_1(self, user: User, scenario: Scenario, message: str | None = None) -> Response:
        step_number = 1
        if message is not None:
            try:
                message_date = datetime.strptime(message, '%d.%m.%Y')
                for step in scenario.steps:
                    if step.number == step_number:
                        step.result = message
                        break
                scenario.current_step = step_number + 1
                await self.repository.scenarios.upsert_user_scenario(user, scenario)
                return await self.step_dispatcher[scenario.current_step](user, scenario)
            except ValueError:
                return await create_calendar_response(
                    messages=[Replies.WRONG_DATE_FORMAT, Replies.ENTER_OR_CHOOSE_DATE],
                    year=datetime.now().year,
                    month=datetime.now().month,
                )
        return await create_calendar_response(
            messages=[Replies.ENTER_OR_CHOOSE_DATE],
            year=datetime.now().year,
            month=datetime.now().month,
        )

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
