import logging

from models import WorkType

from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage
from .google_repository import GoogleRepository

logger = logging.getLogger(__name__)


class WorkTypeRepository:
    _work_type_key = RedisKeys.WORK_TYPES_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        google_repository: GoogleRepository,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.google_repository = google_repository

    async def get_work_types(self) -> list[WorkType]:
        work_types = await self.storage.get_data(
            keys=[self._work_type_key],
        )
        if not work_types:
            await self.google_repository.update_handbooks_data()
            work_types = await self.storage.get_data(keys=[self._work_type_key])

        if not work_types:
            return []

        return [WorkType(**work_type) for work_type in work_types[self._work_type_key]]
