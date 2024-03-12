import logging

from models import User, Scenario, ScenarioStep

from services.constants import RedisKeys
from services.google_sheets_api_service import GoogleSheetsApiService
from services.storage import Storage
from .google_repository import GoogleRepository

logger = logging.getLogger(__name__)


class ScenarioRepository:
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

    async def upsert_user_scenario(self, user: User, scenario: Scenario):
        steps = [step.dict() for step in scenario.steps]
        scenario_dict = scenario.dict()
        scenario_dict['steps'] = steps
        await self.storage.set_data(
            keys=[self._scenario_key, user.chat_id],
            data=scenario_dict,
        )

    async def get_user_scenario(self, user: User) -> Scenario | None:
        scenario_dict = await self.storage.get_data(
            keys=[self._scenario_key, user.chat_id],
        )
        if not scenario_dict:
            return None
        scenario_steps = scenario_dict.pop('steps')
        scenario_steps = [ScenarioStep(**step) for step in scenario_steps]
        scenario = Scenario(**scenario_dict, steps=scenario_steps)
        return scenario
