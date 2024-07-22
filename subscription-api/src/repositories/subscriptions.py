from abc import ABC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.database.models import subscription_table
from src.models.domain.subscription import Subscription
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.subscription import SubscriptionCreateSchema


class SubscriptionsRepositoryABC(RepositoryABC, ABC):
    ...


class SubscriptionsRepository(
    SubscriptionsRepositoryABC,
    SqlAlchemyRepository[Subscription, SubscriptionCreateSchema],
):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Subscription, table=subscription_table)


class CachedSubscriptionsRepository(SubscriptionsRepositoryABC):
    def __init__(self, repo: SubscriptionsRepositoryABC, cache: CacheClientABC):
        self._repo = repo
        self._cache = cache

    async def gets(self) -> PaginatedPage[Subscription]:
        return await self._repo.gets()

    async def get(self, *, entity_id: UUID) -> Subscription:
        key = f"subscruption_{entity_id}"
        entity = await self._cache.get(key=key)
        if entity:
            return Subscription(**entity)
        entity = await self._repo.get(entity_id=entity_id)
        if entity:
            await self._cache.insert(key=key, value=entity)
        return entity

    def insert(self, *, data: SubscriptionCreateSchema) -> Subscription:
        return self._repo.insert(data=data)

    async def delete(self, *, entity_id: UUID):
        key = f"subscruption_{entity_id}"
        await self._repo.delete(entity_id)
        await self._cache.delete(key)
