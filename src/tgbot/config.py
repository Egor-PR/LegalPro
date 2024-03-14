from configparser import ConfigParser
from dataclasses import dataclass
from enum import StrEnum


@dataclass
class GoogleRepositoryConfig:
    spreadsheet_id: str
    users_sheet_name: str
    users_sheet_range: str
    handbook_expire_seconds: int
    work_types_sheet_name: str
    work_types_sheet_range: str
    clients_sheet_name: str
    clients_sheet_range: str


@dataclass
class GoogleSheetsConfig:
    discovery_url: str
    service_name: str
    version: str
    creds_file: str
    scopes: str


@dataclass
class RedisConfig:
    url: str


class LoggerLevel(StrEnum):
    info = 'INFO'
    debug = 'DEBUG'


@dataclass
class LoggerConfig:
    level: LoggerLevel = LoggerLevel.info


@dataclass
class TgBotConfig:
    token: str


@dataclass
class Config:
    logger: LoggerConfig
    tgbot: TgBotConfig
    redis: RedisConfig
    google_sheets: GoogleSheetsConfig
    google_repository: GoogleRepositoryConfig


def load_config(path: str):
    config = ConfigParser()
    config.read(path)

    logger_conf = config['logger']
    tgbot_conf = config['tgbot']
    redis_conf = config['redis']
    google_sheets_conf = config['google_sheets']
    google_repository_conf = config['google_repository']

    return Config(
        logger=LoggerConfig(
            level=logger_conf.get('level'),
        ),
        tgbot=TgBotConfig(
            token=tgbot_conf.get('token'),
        ),
        redis=RedisConfig(
            url=redis_conf.get('url'),
        ),
        google_sheets=GoogleSheetsConfig(
            discovery_url=google_sheets_conf.get('discovery_url'),
            service_name=google_sheets_conf.get('service_name'),
            version=google_sheets_conf.get('version'),
            creds_file=google_sheets_conf.get('creds_file'),
            scopes=google_sheets_conf.get('scopes'),
        ),
        google_repository=GoogleRepositoryConfig(
            spreadsheet_id=google_repository_conf.get('spreadsheet_id'),
            users_sheet_name=google_repository_conf.get('users_sheet_name'),
            users_sheet_range=google_repository_conf.get('users_sheet_range'),
            handbook_expire_seconds=google_repository_conf.get('handbook_expire_seconds'),
            work_types_sheet_name=google_repository_conf.get('work_types_sheet_name'),
            work_types_sheet_range=google_repository_conf.get('work_types_sheet_range'),
            clients_sheet_name=google_repository_conf.get('clients_sheet_name'),
            clients_sheet_range=google_repository_conf.get('clients_sheet_range')
        ),
    )
