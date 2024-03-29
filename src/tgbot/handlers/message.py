import logging
from datetime import datetime

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from models import User, Response, ResponseType, TextMessagesResponse, ReplyKeyboardResponse
from services import Application
from services.scenarios.client_report import ClientReportActCallback

from .utils import SimpleCalendar, CalendarCallback

logger = logging.getLogger(__name__)
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

        try:
            await message.delete_reply_markup()
        except Exception:
            pass

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
            skip_calendar=response.calendar_response.skip_calendar,
        )
        msgs = response.calendar_response.messages
        for i in range(len(msgs)):
            if i + 1 == len(msgs):
                await message.answer(text=msgs[i], reply_markup=rkm)
                continue
            await message.answer(text=msgs[i], reply_markup=ReplyKeyboardRemove())
        return

    if response.type == ResponseType.INLINE_KEYBOARD:
        inline_keyboard = []
        for row in response.inline_keyboard_response.inlines:
            buttons = [
                InlineKeyboardButton(text=button.text, callback_data=button.callback_data)
                for button in row
            ]
            inline_keyboard.append(buttons)

        ikm = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        if response.inline_keyboard_response.delete_reply_keyboard:
            await message.delete_reply_markup()
            return

        if response.inline_keyboard_response.edit_reply_keyboard:
            await message.edit_reply_markup(reply_markup=ikm)
            return

        if response.inline_keyboard_response.delete_reply_keyboard_and_continue:
            await message.delete_reply_markup()

        for i in range(len(response.inline_keyboard_response.messages)):
            if i + 1 == len(response.inline_keyboard_response.messages):
                await message.answer(
                    text=response.inline_keyboard_response.messages[i],
                    reply_markup=ikm,
                    parse_mode='MarkdownV2'
                )
                continue
            await message.answer(
                text=response.inline_keyboard_response.messages[i],
                reply_markup=ReplyKeyboardRemove(),
                parse_mode='MarkdownV2'
            )
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


@messages_router.callback_query(ClientReportActCallback.filter())
async def process_client_report(
    callback_query: CallbackQuery,
    callback_data: ClientReportActCallback,
    user: User | None,
    app: Application,
):
    msg = callback_data.pack()
    response: Response = await app.execute(msg, user, callback_query.from_user.id)
    await process_response(callback_query.message, response)
