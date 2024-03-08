import logging
from typing import Any, cast

from aiogram.fsm.storage.redis import RedisStorage

logger = logging.getLogger(__name__)


class Storage(RedisStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_separator = ':'

    async def build_key(
        self,
        key: list[str],
    ) -> str:
        return self.key_separator.join(key)

    async def set_data(
        self,
        keys: list[str],
        data: dict[str, Any],
        expired: int | None = None,
    ) -> None:
        redis_key = await self.build_key(keys)
        if not data:
            await self.redis.delete(redis_key)
            return
        await self.redis.set(
            redis_key,
            self.json_dumps(data),
            ex=expired,
        )

    async def get_data(
        self,
        keys: list[str],
    ) -> dict[str, Any]:
        _key = await self.build_key(keys)
        value = await self.redis.get(_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return cast(dict[str, Any], self.json_loads(value))
