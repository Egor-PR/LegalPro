import logging
from enum import StrEnum

from models import User, WorkType, Client
from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage

logger = logging.getLogger(__name__)


class SpreadsheetBool(StrEnum):
    yes = 'Да'
    no = 'Нет'


class GoogleRepository:
    _user_list_key = RedisKeys.USERS_LIST_KEY
    _work_types_key = RedisKeys.WORK_TYPES_KEY
    _clients_key = RedisKeys.CLIENTS_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        spreadsheet_id: str,
        users_sheet_name: str,
        users_sheet_range: str,
        handbook_expire_seconds: int,
        work_types_sheet_name: str,
        work_types_sheet_range: str,
        clients_sheet_name: str,
        clients_sheet_range: str,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.spreadsheet_id = spreadsheet_id
        self.users_sheet_name = users_sheet_name
        self.users_sheet_range = users_sheet_range
        self.handbook_expire_seconds = handbook_expire_seconds
        self.work_types_sheet_name = work_types_sheet_name
        self.work_types_sheet_range = work_types_sheet_range
        self.clients_sheet_name = clients_sheet_name
        self.clients_sheet_range = clients_sheet_range

    async def update_handbooks_data(self):
        data = [
            (self.users_sheet_name, self.users_sheet_range,),
            (self.work_types_sheet_name, self.work_types_sheet_range,),
            (self.clients_sheet_name, self.clients_sheet_range,)
        ]

        google_ranges = self.google_sheet_service.get_ranges(
            spreadsheet_id=self.spreadsheet_id,
            ranges=data,
        )

        if len(google_ranges) != len(data):
            raise ValueError(f'Google ranges count is not equal {len(data)}')

        # Users
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

        # Work types
        work_types_range = google_ranges[1]
        work_types = []
        for work_type_row in work_types_range:
            work_type = await self._parse_work_type_row(work_type_row)
            if work_type:
                work_types.append(work_type)

        await self.storage.set_data(
            keys=[self._work_types_key],
            data={self._work_types_key: [work_type.dict() for work_type in work_types]},
            expired=self.handbook_expire_seconds,
        )

        # Clients
        clients_range = google_ranges[2]
        clients = []
        for client_row in clients_range:
            client = await self._parse_client_row(client_row)
            if client:
                clients.append(client)

        await self.storage.set_data(
            keys=[self._clients_key],
            data={self._clients_key: [client.dict() for client in clients]},
            expired=self.handbook_expire_seconds,
        )

    async def _parse_client_row(self, client_row: list[str]) -> str | None:
        if len(client_row) < 2:
            logger.warning(f'Client row is too short: {client_row}')
            return None

        if not client_row[0]:
            logger.warning(f'Client name is empty: {client_row}')
            return None

        if client_row[1] not in [SpreadsheetBool.yes, SpreadsheetBool.no]:
            logger.warning(f'Client completed field is not valid: {client_row}')
            return None

        return Client(
            name=client_row[0],
            completed=client_row[1] == SpreadsheetBool.yes,
        )

    async def _parse_work_type_row(self, work_type_row: list[str]) -> str | None:
        if len(work_type_row) < 1:
            logger.warning(f'Work type row is too short: {work_type_row}')
            return None

        if not work_type_row[0]:
            logger.warning(f'Work type name is empty: {work_type_row}')
            return None

        return WorkType(name=str(work_type_row[0]))

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
