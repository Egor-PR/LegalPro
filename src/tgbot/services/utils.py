import logging

from models import InlineKeyboardResponse, InlineButton
from models import ReplyCalendarResponse
from models import Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse

logger = logging.getLogger(__name__)


async def create_inline_keyboard_response(
    messages: list[str],
    buttons: list[list[tuple[str, str]]],
    delete_reply_keyboard: bool = False,
    edit_reply_keyboard: bool = False,
    delete_reply_keyboard_and_continue: bool = False,
):
    _buttons = [
        [
            InlineButton(text=text, callback_data=callback_data)
            for text, callback_data in button_row
        ]
        for button_row in buttons
    ]
    inline_keyboard_resp = InlineKeyboardResponse(
        messages=messages,
        inlines=_buttons,
        delete_reply_keyboard=delete_reply_keyboard,
        edit_reply_keyboard=edit_reply_keyboard,
        delete_reply_keyboard_and_continue=delete_reply_keyboard_and_continue,
    )
    return Response(
        type=ResponseType.INLINE_KEYBOARD,
        inline_keyboard_response=inline_keyboard_resp,
    )


async def create_calendar_response(
    messages: list[str],
    year: int,
    month: int,
    skip_calendar: bool = False,
) -> Response:
    calendar_resp = ReplyCalendarResponse(
        messages=messages,
        year=year,
        month=month,
        skip_calendar=skip_calendar,
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
