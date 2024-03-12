import logging
import json

from services.storage import Storage
from models import User
from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService

from .google_repository import GoogleRepository

logger = logging.getLogger(__name__)


class UserRepository:
    _user_list_key = RedisKeys.USERS_LIST_KEY
    _user_key = RedisKeys.USER_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        google_repository: GoogleRepository,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.google_repository = google_repository

    async def get_user_by_chat_id(self, chat_id: int) -> User | None:
        _user = None
        user_dict = await self.storage.get_data(
            keys=[self._user_key, str(chat_id)],
        )
        if not user_dict:
            return _user

        try:
            _user = User(**user_dict)
        except Exception as exc:
            logger.exception(exc)
            return _user

        _user_from_sheet = await self.get_user_by_code(_user.id)
        if _user_from_sheet and not _user_from_sheet.is_active:
            await self.storage.set_data(keys=[self._user_key, str(chat_id)])
            return None

        return _user

    async def get_user_by_code(self, user_code: str) -> User | None:
        users = await self.get_users()
        for user in users:
            if user.id == user_code and user.is_active:
                return user
        return None

    async def upsert(self, user: User) -> None:
        if not user.chat_id:
            raise ValueError('User chat_id is required to upsert user')
        await self.storage.set_data(
            keys=[self._user_key, str(user.chat_id)],
            data=user.dict(),
        )

    async def get_users(self) -> list[User]:
        users_dict = await self.storage.get_data(keys=[self._user_list_key])
        if not users_dict:
            await self.google_repository.update_handbooks_data()
            users_dict = await self.storage.get_data(keys=[self._user_list_key])
        users_list = users_dict.get(self._user_list_key, [])
        users = []
        for users_dict in users_list:
            try:
                users.append(User(**users_dict))
            except Exception as exc:
                logger.exception(exc)
                continue
        return users
