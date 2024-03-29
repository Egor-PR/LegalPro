import logging

from models import Client

from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage
from .google_repository import GoogleRepository

logger = logging.getLogger(__name__)


class ClientRepository:
    _clients_key = RedisKeys.CLIENTS_KEY

    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        google_repository: GoogleRepository,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.google_repository = google_repository

    async def get_clients(self, is_completed: bool | None = None) -> list[Client]:
        clients = await self.storage.get_data(
            keys=[self._clients_key],
        )
        if not clients:
            await self.google_repository.update_handbooks_data()
            clients = await self.storage.get_data(keys=[self._clients_key])
        if not clients:
            return []
        clients = [Client(**client) for client in clients[self._clients_key]]
        if is_completed is not None:
            clients = list(filter(lambda x: x.completed == is_completed, clients))
        return clients
