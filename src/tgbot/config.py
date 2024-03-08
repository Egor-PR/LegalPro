from configparser import ConfigParser
from dataclasses import dataclass
from enum import StrEnum


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


def load_config(path: str):
    config = ConfigParser()
    config.read(path)

    logger_conf = config['logger']
    tgbot_conf = config['tgbot']
    redis_conf = config['redis']
    google_sheets_conf = config['google_sheets']

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
    )
