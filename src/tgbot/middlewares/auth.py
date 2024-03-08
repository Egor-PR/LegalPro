import logging

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services import Application, Storage

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    def __init__(self, storage: Storage):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        app: Application = data['dispatcher'].get('app')
        chat_id = event.chat.id
        user = await app.auth(chat_id)
        data.update({'user': user if user else None})
        return await handler(event, data)
