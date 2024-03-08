import logging

from models import User, Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse
from .constants import Replies, MenuButtons
from .repostiories import Repository

logger = logging.getLogger(__name__)


async def create_reply_keyboard_response(
    messages: list[str],
    buttons: list[list[str]],
    is_persistent: bool | None = None,
    resize_keyboard: bool | None = None,
    one_time_keyboard: bool | None = None,
    input_field_placeholder: bool | None = None,
) -> Response:
    reply_keyboard_resp = ReplyKeyboardResponse(
        messages=messages,
        buttons=buttons,
        is_persistent=is_persistent,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
        input_field_placeholder=input_field_placeholder,
    )
    return Response(
        type=ResponseType.LIST_REPLY_KEYBOARD,
        reply_keyboard_response=reply_keyboard_resp,
    )


async def create_message_response(messages: list[str]) -> Response:
    message_response = TextMessagesResponse(messages=messages)
    return Response(
        type=ResponseType.TEXT_MESSAGES,
        message_response=message_response,
    )


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
            return await create_message_response([Replies.PLEASE_AUTH, Replies.ENTER_PERSONAL_CODE])
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
        return await self.menu(user)
