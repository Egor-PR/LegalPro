import logging

from models import User, Response, ResponseType, ReplyKeyboardResponse, TextMessagesResponse, Scenario, ScenarioStep
from services.constants import Replies, MenuButtons
from services.repostiories import Repository

logger = logging.getLogger(__name__)


class ClientReportScenario:
    name = 'client_report'
    
    def __init__(self, repository: Repository):
        self.repository = repository

    async def prologue(self, message: str, user: User, user_scenario: Scenario) -> Response:
        """First step of scenario"""
        pass
