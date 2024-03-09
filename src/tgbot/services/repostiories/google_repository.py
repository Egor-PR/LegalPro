import logging
from enum import StrEnum

from models import User
from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage

logger = logging.getLogger(__name__)


class SpreadsheetBool(StrEnum):
    yes = 'Да'
    no = 'Нет'


class GoogleRepository:
    _user_list_key = RedisKeys.USERS_LIST_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        spreadsheet_id: str,
        users_sheet_name: str,
        users_sheet_range: str,
        handbook_expire_seconds: int,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.spreadsheet_id = spreadsheet_id
        self.users_sheet_name = users_sheet_name
        self.users_sheet_range = users_sheet_range
        self.handbook_expire_seconds = handbook_expire_seconds

    async def update_handbooks_data(self):
        data = [
            (self.users_sheet_name, self.users_sheet_range,)
        ]

        google_ranges = self.google_sheet_service.get_ranges(
            spreadsheet_id=self.spreadsheet_id,
            ranges=data,
        )

        if len(google_ranges) != len(data):
            raise ValueError(f'Google ranges count is not equal {len(data)}')

        users_range = google_ranges[0]
        users = []
        for user_row in users_range:
            user = await self._parse_user_row(user_row)
            if user:
                users.append(user)

        await self.storage.set_data(
            keys=[self._user_list_key],
            data={self._user_list_key: [user.dict() for user in users]},
            expired=self.handbook_expire_seconds,
        )

    async def _parse_user_row(self, user_row: list[str]) -> User | None:
        row_min_len = 5
        if len(user_row) < row_min_len:
            logger.warning(f'User row is too short: {user_row}')
            return None

        return User(
            fullname=user_row[0],
            job_title=user_row[1],
            id=user_row[2],
            admin=user_row[3] == SpreadsheetBool.yes,
            is_active=user_row[4] == SpreadsheetBool.yes,
        )