from services.storage import Storage
from services.google_sheets_api_service import GoogleSheetsApiService

from .user_repository import UserRepository


class Repository:
    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.users = UserRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
        )
