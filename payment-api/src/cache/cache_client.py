import json
from abc import ABC, abstractmethod

import backoff
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from src.core.settings import BACKOFF_CONFIG
from src.models.domain.base import DomainBase


class CacheClientABC(ABC):
    @abstractmethod
    async def get(self, *, key: str) -> dict | None:
        ...

    @abstractmethod
    async def insert(self, *, key: str, value: DomainBase) -> None:
        ...

    @abstractmethod
    async def delete(self, *keys) -> None:
        ...


class RedisCacheClient(CacheClientABC):
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def get(self, *, key: str) -> dict | None:
        data = await self._redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def insert(self, *, key: str, value: DomainBase):
        await self._redis_client.set(
            name=key, value=json.dumps(jsonable_encoder(value))
        )

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def delete(self, *keys) -> None:
        await self._redis_client.delete(*keys)
