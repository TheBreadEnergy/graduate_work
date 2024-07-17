import json
from abc import ABC, abstractmethod

from redis.asyncio import Redis
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

    async def get(self, *, key: str) -> dict | None:
        data = await self._redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def insert(self, *, key: str, value: DomainBase):
        await self._redis_client.set(name=key, value=value.model_dump_json())

    async def delete(self, *keys) -> None:
        await self._redis_client.delete(*keys)
