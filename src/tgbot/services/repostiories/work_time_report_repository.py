import logging

from models import User, WorkTimeReportStat, WorkTimeReport
from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage
from .google_repository import GoogleRepository

logger = logging.getLogger(__name__)


class WorkTimeReportRepository:
    _work_time_report_key = RedisKeys.WORK_TIME_REPORT_KEY
    _work_time_report_stat_key = RedisKeys.WORK_TIME_REPORT_STAT_KEY
    _scenario_key = RedisKeys.SCENARIO_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        google_repository: GoogleRepository,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.google_repository = google_repository

    async def delete_report(self, report_id: int) -> bool:
        return await self.google_repository.mark_report_removed(report_id)

    async def remove_reports_from_cache(self, user: User):
        await self.storage.del_keys([
            [self._work_time_report_key, user.chat_id],
            [self._work_time_report_stat_key, user.chat_id],
        ])

    async def delete_scenario_and_reports_from_cache(self, user: User):
        await self.storage.del_keys([
            [self._scenario_key, user.chat_id],
            [self._work_time_report_key, user.chat_id],
            [self._work_time_report_stat_key, user.chat_id],
        ])

    async def get_stats(
        self,
        user: User,
        report_date: str,
        client: str | None = None,
    ) -> WorkTimeReportStat:
        keys = [self._work_time_report_stat_key, user.chat_id]
        stats = await self.storage.get_data(keys=keys)
        if not stats:
            await self.google_repository.update_work_time_report_data(user, report_date, client)
            stats = await self.storage.get_data(keys=keys)

        if not stats:
            stats = {
                self._work_time_report_stat_key: {
                    'report_date': report_date,
                },
            }

        return WorkTimeReportStat(**stats[self._work_time_report_stat_key])

    async def get_reports(
        self,
        user: User,
        report_date: str,
        client: str | None = None,
    ) -> list[WorkTimeReport]:
        keys = [self._work_time_report_key, user.chat_id]
        reports = await self.storage.get_data(keys=keys)
        if not reports:
            await self.google_repository.update_work_time_report_data(user, report_date, client)
            reports = await self.storage.get_data(keys=keys)

        if not reports:
            return []

        return [WorkTimeReport(**report) for report in reports[self._work_time_report_key]]
