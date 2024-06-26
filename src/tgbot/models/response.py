from dataclasses import dataclass
from enum import StrEnum


class ResponseType(StrEnum):
    TEXT_MESSAGES = "text_messages"
    LIST_REPLY_KEYBOARD = "list_reply_keyboard"
    INLINE_KEYBOARD = "inline_keyboard"
    CALENDAR = "calendar"


@dataclass
class InlineButton:
    text: str
    callback_data: str


@dataclass
class InlineKeyboardResponse:
    messages: list[str]
    inlines: list[list[InlineButton]]
    delete_reply_keyboard: bool = False
    edit_reply_keyboard: bool = False
    delete_reply_keyboard_and_continue: bool = False


@dataclass
class ReplyCalendarResponse:
    messages: list[str]
    year: int
    month: int
    skip_calendar: bool = False


@dataclass
class ReplyKeyboardResponse:
    messages: list[str]
    buttons: list[list[str]]
    is_persistent: bool | None = None
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None
    input_field_placeholder: bool | None = None


@dataclass
class TextMessagesResponse:
    messages: list[str]


@dataclass
class Response:
    type: ResponseType
    message_response: TextMessagesResponse | None = None
    reply_keyboard_response: ReplyKeyboardResponse | None = None
    calendar_response: ReplyCalendarResponse | None = None
    inline_keyboard_response: InlineKeyboardResponse | None = None


@dataclass
class FinalResponse:
    pass
