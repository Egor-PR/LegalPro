import logging

from models import Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse
from models import ReplyCalendarResponse

logger = logging.getLogger(__name__)


async def create_calendar_response(
    messages: list[str],
    year: int,
    month: int,
) -> Response:
    calendar_resp = ReplyCalendarResponse(
        messages=messages,
        year=year,
        month=month,
    )
    return Response(
        type=ResponseType.CALENDAR,
        calendar_response=calendar_resp,
    )


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
