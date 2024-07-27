from abc import ABC, abstractmethod
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import and_, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.database.models import user_subscription_table
from src.models.domain.user_subscription import UserSubscription
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.user_subscription import UserSubscriptionCreateSchema


class UserSubscriptionsRepositoryABC(RepositoryABC, ABC):
    """
    Интерфейс репозитория для пользовательских подписок.
    Нужен для спецификации базового интерфейса. Наследуется и расширяет интерфейс RepositoryABC добавляя методы
    get_user_subscriptions, для получения подписок конкретного пользователя  и get_filtered_subscriptions для получения
    фильтрованного списка пользовательских подписок по активности
    """

    @abstractmethod
    async def get_user_subscriptions(
        self, *, user_id: UUID, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        ...

    @abstractmethod
    async def get_filtered_subscriptions(
        self, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        ...


class UserSubscriptionsRepository(
    UserSubscriptionsRepositoryABC,
    SqlAlchemyRepository[UserSubscription, UserSubscriptionCreateSchema],
):
    """
    Конкретная реализация интерфейса UserSubscriptionsRepositoryABC.
    Реaлизация методов репозитория наследуется от конкретного  специфицированного шаблонного класса
    SqlAlchemyRepository, добавляя реализацию методов специфичных для UserSubscriptionRepositoryABC
    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, model=UserSubscription, table=user_subscription_table
        )

    async def get_user_subscriptions(
        self, *, user_id: UUID, active: bool | None = None
    ) -> PaginatedPage:
        query = select(UserSubscription).where(
            and_(
                self._table.c.user_id == user_id,
                self._table.c.active == active if active is not None else true(),
            )
        )
        return await paginate(self._session, query)

    async def get_filtered_subscriptions(
        self, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        query = select(UserSubscription).where(
            self._table.c.active == active if active is not None else true(),
        )
        return await paginate(self._session, query)


class CachedUserSubscriptionsRepository(UserSubscriptionsRepositoryABC):
    """
    Конкретная реализация интерфейса UserSubscriptionsRepositoryABC с добавлением функциональности кеширования.
    Является декоратором над репозиторием реализующим UserSubscriptionRepositoryABC и RepositoryABC
    (UserSubscriptionRepository)
    """

    def __init__(self, repo: UserSubscriptionsRepositoryABC, cache: CacheClientABC):
        self._repo = repo
        self._cache = cache

    async def get_filtered_subscriptions(
        self, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        return await self._repo.get_filtered_subscriptions(active=active)

    async def get_user_subscriptions(
        self, *, user_id: UUID, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        return await self._repo.get_user_subscriptions(user_id=user_id)

    async def gets(self) -> PaginatedPage[UserSubscription]:
        return await self._repo.gets()

    async def get(self, *, entity_id: UUID) -> UserSubscription | None:
        key = f"user_subscription_{entity_id}"
        entity = await self._cache.get(key=key)
        if entity:
            return UserSubscription(**entity)
        entity = await self._repo.get(entity_id=entity_id)
        if entity:
            await self._cache.insert(key=key, value=entity)
        return entity

    def insert(self, *, data: UserSubscriptionCreateSchema) -> UserSubscription:
        return self._repo.insert(data=data)

    async def delete(self, *, entity_id: UUID):
        key = f"user_subscription_{entity_id}"
        await self._repo.delete(entity_id=entity_id)
        await self._cache.delete(key)
