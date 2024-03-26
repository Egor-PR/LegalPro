import asyncio
import logging
from enum import StrEnum

from models import User, WorkType, Client, Scenario, ScenarioStep, WorkTimeReport
from models import WorkTimeReportStat
from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage

logger = logging.getLogger(__name__)


class NotSetFilterError(Exception):
    pass


class LockTimeoutError(Exception):
    pass


class SpreadsheetBool(StrEnum):
    yes = 'Да'
    no = 'Нет'


class GoogleRepository:
    _user_list_key = RedisKeys.USERS_LIST_KEY
    _work_types_key = RedisKeys.WORK_TYPES_KEY
    _clients_key = RedisKeys.CLIENTS_KEY
    _work_time_report_key = RedisKeys.WORK_TIME_REPORT_KEY
    _work_time_report_stat_key = RedisKeys.WORK_TIME_REPORT_STAT_KEY
    _work_time_report_lock_key = RedisKeys.WORK_TIME_REPORT_LOCK_KEY

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
        work_time_report_sheet_name: str,
        work_time_report_sheet_range: str,
        wtrs_sheet_name: str,
        wtrs_sheet_range: str,
        wtrs_date_cell: str,
        wtrs_user_cell: str,
        wtrs_client_cell: str,
        wtrs_time_plan_cell: str,
        wtrs_time_fact_cell: str,
        wtrs_time_net_cell: str,
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
        self.work_time_report_sheet_name = work_time_report_sheet_name
        self.work_time_report_sheet_range = work_time_report_sheet_range
        self.wtrs_sheet_name = wtrs_sheet_name
        self.wtrs_sheet_range = wtrs_sheet_range
        self.wtrs_date_cell = wtrs_date_cell
        self.wtrs_user_cell = wtrs_user_cell
        self.wtrs_client_cell = wtrs_client_cell
        self.wtrs_time_plan_cell = wtrs_time_plan_cell
        self.wtrs_time_fact_cell = wtrs_time_fact_cell
        self.wtrs_time_net_cell = wtrs_time_net_cell
        self._lock_attempt_count = 10

    async def update_work_time_report_data(
        self,
        user: User,
        report_date: str,
        client: str | None = None,
    ):
        await self._set_lock(self._work_time_report_lock_key)
        update_data = {
            self.wtrs_sheet_name: {
                f'{self.wtrs_date_cell}:{self.wtrs_date_cell}': [[report_date]],
                f'{self.wtrs_user_cell}:{self.wtrs_user_cell}': [[user.id]],
            }
        }
        if client:
            update_data[self.wtrs_sheet_name].update(
                {
                    f'{self.wtrs_client_cell}:{self.wtrs_client_cell}': [[client]]
                }
            )

        set_filter_result = self.google_sheet_service.update_many(
            spreadsheet_id=self.spreadsheet_id,
            data=update_data,
        )
        if not set_filter_result:
            logger.warning(f'Error while setting filter for work time report '
                           f'{user}, {report_date}, {client}')
            await self._delete_lock(self._work_time_report_lock_key)
            raise NotSetFilterError

        get_data = [
            (self.wtrs_sheet_name, self.wtrs_sheet_range,),
            (self.wtrs_sheet_name, f'{self.wtrs_time_plan_cell}:{self.wtrs_time_net_cell}',),
            (self.wtrs_sheet_name, f'{self.wtrs_time_fact_cell}:{self.wtrs_time_fact_cell}',),
            (self.wtrs_sheet_name, f'{self.wtrs_time_net_cell}:{self.wtrs_time_net_cell}',),
        ]

        google_ranges = self.google_sheet_service.get_ranges(
            spreadsheet_id=self.spreadsheet_id,
            ranges=get_data,
        )
        logger.info(f'Google ranges: {google_ranges}')
        if len(google_ranges) != len(get_data):
            logger.error(f'Google ranges count is not equal {len(get_data)}')
            await self._delete_lock(self._work_time_report_lock_key)
            raise ValueError(f'Google ranges count is not equal {len(get_data)}')

        raw_reports = google_ranges[0]
        time_plan = google_ranges[1]
        time_fact = google_ranges[2]
        time_net = google_ranges[3]

        reports = []
        for report_row in raw_reports:
            report = await self._parse_work_time_report_row(report_row)
            if report:
                reports.append(report)
        await self.storage.set_data(
            keys=[self._work_time_report_key, user.chat_id],
            data={self._work_time_report_key: [report.dict() for report in reports]},
            expired=300,  # TODO: move to constants
        )

        try:
            if len(time_plan) == 1 and len(time_plan[0]) == 1:
                time_plan = time_plan[0][0]
            else:
                time_plan = None
            if len(time_fact) == 1 and len(time_fact[0]) == 1:
                time_fact = time_fact[0][0]
            else:
                time_fact = None
            if len(time_net) == 1 and len(time_net[0]) == 1:
                time_net = time_net[0][0]
            else:
                time_net = None
            stat = WorkTimeReportStat(
                time_plan=time_plan,
                time_fact=time_fact,
                time_net=time_net,
                report_date=report_date,
            )
            await self.storage.set_data(
                keys=[self._work_time_report_stat_key, user.chat_id],
                data={self._work_time_report_stat_key: stat.dict()},
                expired=300,  # TODO: move to constants
            )
        except IndexError:
            logger.warning(f'Error while parsing time plan, time fact, time net')
            await self._delete_lock(self._work_time_report_lock_key)
            raise ValueError(f'Error while parsing time plan, time fact, time net')

        await self._delete_lock(self._work_time_report_lock_key)

    async def append_work_time_report(self, report: WorkTimeReport) -> bool:
        data = [report.get_list()]
        return self.google_sheet_service.append(
            spreadsheet_id=self.spreadsheet_id,
            sheet_name=self.work_time_report_sheet_name,
            sheet_range=self.work_time_report_sheet_range,
            data=data,
        )

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

    async def _parse_work_time_report_row(self, report_row: list[str]) -> WorkTimeReport | None:
        if len(report_row) < 9:
            logger.warning(f'Work time report row is too short: {report_row}')
            return None

        try:
            row_id = int(report_row[8])
        except ValueError:
            logger.warning(f'Work time report row id is not valid: {report_row}')
            return None

        return WorkTimeReport(
            report_date=report_row[0],
            user_id=report_row[1],
            user_fullname=report_row[2],
            user_job_title=report_row[3],
            work_type=report_row[4],
            client=report_row[5],
            hours=report_row[6],
            comment=report_row[7],
            row_id=row_id,
        )

    async def _set_lock(self, lock_key: str):
        attempt_count = 0
        while True:
            lock = await self.storage.get_data(keys=[lock_key])
            if lock:
                attempt_count += 1
                if attempt_count >= self._lock_attempt_count:
                    logger.warning(f'Lock timeout for work time report '
                                   f'{user}, {report_date}, {client}')
                    raise LockTimeoutError
                await asyncio.sleep(1)
                continue
            await self.storage.set_data(
                keys=[lock_key],
                data={lock_key: True},
                expired=30,  # TODO: move to constants
            )
            break

    async def _delete_lock(self, lock_key: str):
        await self.storage.set_data(keys=[lock_key], data={})

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
