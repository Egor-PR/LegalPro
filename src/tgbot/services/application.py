import logging

from models import User, Response

from .constants import Replies, MenuButtons
from .repostiories import Repository
from .scenarios import ClientReportScenario, WorkTimeReportScenario
from .utils import create_reply_keyboard_response, create_message_response

logger = logging.getLogger(__name__)


class Application:
    def __init__(self, repository: Repository):
        self.repository = repository

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

    async def authenticate(self, user_code: str, chat_id: int | None = None) -> Response:
        user = await self.repository.users.get_user_by_code(user_code)
        if user is None:
            return await create_message_response([
                Replies.WRONG_PERSONAL_CODE, Replies.PLEASE_AUTH, Replies.ENTER_PERSONAL_CODE
            ])
        user.chat_id = chat_id
        await self.repository.users.upsert(user)
        return await self.menu(user)

    async def execute(
        self,
        user_message: str,
        user: User | None,
        chat_id: int | None = None,
    ) -> Response:
        if user is None:
            return await self.authenticate(user_message, chat_id)

        user_scenario = await self.repository.scenarios.get_user_scenario(user)

        if user_scenario and user_scenario.name == WorkTimeReportScenario.name:
            return await WorkTimeReportScenario(self.repository).prologue(
                user_message, user, user_scenario
            )
        elif user_scenario and user_scenario.name == ClientReportScenario.name:
            return await ClientReportScenario(self.repository).prologue(
                user_message, user, user_scenario
            )

        if user_message == MenuButtons.TIME_REPORT:
            return await WorkTimeReportScenario(self.repository).prologue(user_message, user)
        elif user_message == MenuButtons.CLIENT_REPORT:
            pass

        return await self.menu(user)
