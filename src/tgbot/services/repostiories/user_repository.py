import logging
import json

from services.storage import Storage
from models import User
from services.google_sheets_api_service import GoogleSheetsApiService

logger = logging.getLogger(__name__)


class UserRepository:
    _user_list_key = 'users'
    _user_key = 'user'

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        user_dict = await self.storage.get_data(
            keys=[self._user_key, str(chat_id)],
        )
        if not user_dict:
            return None

        try:
            return User(**user_dict)
        except Exception as exc:
            logger.exception(exc)
            return None

    async def get_user_by_code(self, user_code: str) -> User | None:
        users_dict = await self.storage.get_data(keys=[self._user_list_key])
        if not users_dict:
            # TODO: go to google sheets and upload users to storage
            pass
        users_list = users_dict.get(self._user_list_key, [])
        for user_dict in users_list:
            if user_dict.get('id') == user_code:
                return User(**user_dict)
        return None

    async def upsert(self, user: User) -> None:
        if not user.chat_id:
            raise ValueError('User chat_id is required to upsert user')
        await self.storage.set_data(
            keys=[self._user_key, str(user.chat_id)],
            data=user.dict(),
        )
