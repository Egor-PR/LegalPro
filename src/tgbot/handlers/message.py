from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from models import User, Response, ResponseType, TextMessagesResponse, ReplyKeyboardResponse
from services import Application

messages_router = Router(name=__name__)


@messages_router.message()
async def message_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.execute(message.text, user, message.from_user.id)

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
        for text in response.reply_keyboard_response.messages:
            await message.answer(text, reply_markup=rkm)
        return
