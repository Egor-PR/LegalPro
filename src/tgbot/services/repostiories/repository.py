from services.storage import Storage
from services.google_sheets_api_service import GoogleSheetsApiService

from .google_repository import GoogleRepository
from .user_repository import UserRepository
from .scenario_repository import ScenarioRepository
from .work_type_repository import WorkTypeRepository
from .client_repository import ClientRepository
from .work_time_report_repository import WorkTimeReportRepository


class Repository:
    def __init__(
        self,
        storage: Storage,
        google_sheet_service: GoogleSheetsApiService,
        google_repository: GoogleRepository,
    ):
        self.storage = storage
        self.google_sheet_service = google_sheet_service
        self.google_repository = google_repository
        self.users = UserRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
            google_repository=google_repository,
        )
        self.scenarios = ScenarioRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
            google_repository=google_repository,
        )
        self.work_types = WorkTypeRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
            google_repository=google_repository,
        )
        self.clients = ClientRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
            google_repository=google_repository,
        )
        self.work_time_reports = WorkTimeReportRepository(
            storage=storage,
            google_sheet_service=google_sheet_service,
            google_repository=google_repository,
        )
