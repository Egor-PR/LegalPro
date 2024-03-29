from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message, BotCommand

from models import User, Response, ResponseType, TextMessagesResponse, ReplyKeyboardResponse
from services import Application
from .message import process_response


class BotCommands:
    start = BotCommand(command='start', description='В меню')
    reset = BotCommand(command='reset', description='Начать с начала')
    back = BotCommand(command='back', description='Шаг назад')
    logout = BotCommand(command='logout', description='Выход')

    @classmethod
    def get_list(cls) -> list[BotCommand]:
        return [
            cls.start,
            cls.reset,
            cls.back,
            cls.logout
        ]


commands_router = Router(name=__name__)


@commands_router.message(Command(BotCommands.start))
async def start_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.start(user)
    await process_response(message, response)


@commands_router.message(Command(BotCommands.back))
async def back_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.back(user)
    await process_response(message, response)


@commands_router.message(Command(BotCommands.reset))
async def reset_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.reset(user)
    await process_response(message, response)


@commands_router.message(Command(BotCommands.logout))
async def logout_handler(message: Message, user: User | None, app: Application) -> None:
    response: Response = await app.logout(user)
    await process_response(message, response)
