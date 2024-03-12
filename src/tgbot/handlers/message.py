from datetime import datetime

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from models import User, Response, ResponseType, TextMessagesResponse, ReplyKeyboardResponse
from services import Application

from .utils import SimpleCalendar, CalendarCallback

messages_router = Router(name=__name__)


async def process_response(message: Message, response: Response):
    if response.type == ResponseType.TEXT_MESSAGES:
        for text in response.message_response.messages:
            await message.answer(text, reply_markup=ReplyKeyboardRemove())
        return

    if response.type == ResponseType.LIST_REPLY_KEYBOARD:
        buttons: list[list[KeyboardButton]] = [
            [KeyboardButton(text=button) for button in button_row]
            for button_row in response.reply_keyboard_response.buttons
        ]
        rkm: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=response.reply_keyboard_response.resize_keyboard,
        )
        msgs = response.reply_keyboard_response.messages
        for i in range(len(msgs)):
            if i + 1 == len(msgs):
                await message.answer(text=msgs[i], reply_markup=rkm)
                continue
            await message.answer(text=msgs[i], reply_markup=ReplyKeyboardRemove())
        return

    if response.type == ResponseType.CALENDAR:
        rkm = await SimpleCalendar().start_calendar(
            year=response.calendar_response.year,
            month=response.calendar_response.month,
        )
        msgs = response.calendar_response.messages
        for i in range(len(msgs)):
            if i + 1 == len(msgs):
                await message.answer(text=msgs[i], reply_markup=rkm)
                continue
            await message.answer(text=msgs[i], reply_markup=ReplyKeyboardRemove())
        return

    await message.answer('Мне нечего тебе ответить')
    raise ValueError(f'Unknown response type: {response.type}')


@messages_router.message()
async def message_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.execute(message.text, user, message.from_user.id)
    await process_response(message, response)


@messages_router.callback_query(CalendarCallback.filter())
async def process_simple_calendar(
    callback_query: CallbackQuery,
    callback_data: dict,
    user: User | None,
    app: Application,
):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected and isinstance(date, datetime):
        msg = date.strftime("%d.%m.%Y")
    elif selected and isinstance(date, str):
        msg = date
    else:
        msg = ''
    try:
        await callback_query.message.answer(f'{msg}')
    except TelegramBadRequest:
        return
    response: Response = await app.execute(msg, user, callback_query.from_user.id)
    await process_response(callback_query.message, response)
