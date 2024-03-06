from configparser import ConfigParser
from dataclasses import dataclass
from enum import StrEnum


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


def load_config(path: str):
    config = ConfigParser()
    config.read(path)

    logger_conf = config['logger']
    tgbot_conf = config['tgbot']
    redis_conf = config['redis']

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
    )
