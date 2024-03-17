import logging
from abc import ABC, abstractmethod

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove

from models import User

logger = logging.getLogger(__name__)


class AbstractNotifier(ABC):
    @abstractmethod
    async def notify(self, message: str, user: User) -> None:
        pass


class TelegramBotNotifier(AbstractNotifier):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify(self, message: str, user: User) -> None:
        if user.chat_id is None:
            logger.warning(f'User {user.fullname} has no chat_id to send a notify message')
            return

        await self.bot.send_message(
            chat_id=user.chat_id,
            text=message,
            parse_mode='MarkdownV2',
            reply_markup=ReplyKeyboardRemove(),
        )
        logger.info(f'Notify message has been sent to user {user.fullname}')
