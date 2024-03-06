import logging
from typing import Any, cast

from aiogram.fsm.storage.redis import RedisStorage

logger = logging.getLogger(__name__)


class Storage(RedisStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_data(
        self,
        key: str,
    ) -> dict[str, Any]:
        value = await self.redis.get(key)
        logger.info(key)
        logger.info(value)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return cast(dict[str, Any], self.json_loads(value))
