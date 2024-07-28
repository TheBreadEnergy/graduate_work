from abc import abstractmethod
from uuid import UUID

import backoff
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.core.settings import BACKOFF_CONFIG
from src.database.models import refunds_table
from src.enums.payment import PaymentStatus
from src.models.domain.refund import Refund
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.refunds import RefundCreateSchema


class RefundRepositoryABC(RepositoryABC):
    """
    Интерфейс репозитория для пользовательских возвратов.
    Нужен для спецификации базового интерфейса. Наследуется и расширяет интерфейс RepositoryABC
    добавляя метод filter_by_status для получения фильтрованного списка пользовательских возвратов по статусу
    """

    @abstractmethod
    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        ...

    @abstractmethod
    async def get_by_external(self, *, refund_id: UUID) -> Refund:
        ...


class RefundRepository(
    RefundRepositoryABC, SqlAlchemyRepository[Refund, RefundCreateSchema]
):
    """
    Конкретная реализация интерфейса RefundRepositoryABC.
    Реaлизация методов репозитория наследуется от конкретного  специфицированного шаблонного класса
    SqlAlchemyRepository, добавляя реализацию методов специфичных для RefundRepositoryABC
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Refund, table=refunds_table)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        query = select(Refund).where(self._table.c.status == status)
        return await paginate(self._session, query)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def get_by_external(self, *, refund_id: UUID) -> Refund:
        query = select(Refund).where(self._table.c.refund_id == refund_id)
        return await paginate(self._session, query)


class CachedRefundRepository(RefundRepositoryABC):
    """
    Конкретная реализация интерфейса RefundRepositoryABC с добавлением функциональности кеширования.
    Является декоратором над репозиторием реализующим RefundRepositoryABC (RefundRepository)
    """

    def __init__(self, repo: RefundRepositoryABC, cache: CacheClientABC):  # noqa
        self._repo = repo
        self._cache = cache
        self._key_entity_prefix = Refund.__name__

    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        return await self._repo.filter_by_status(status=status)

    async def get(self, *, entity_id: UUID) -> Refund | None:
        key = f"{self._key_entity_prefix}_{entity_id}"
        obj = await self._cache.get(key=key)
        if obj:
            return Refund(**obj)
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity

    async def gets(self, *, account_id: UUID | None = None) -> PaginatedPage[Refund]:
        return await self._repo.gets(account_id=account_id)

    async def get_by_external(self, *, refund_id: UUID) -> Refund:
        return await self._repo.get_by_external(refund_id=refund_id)

    async def insert(self, *, data: RefundCreateSchema) -> Refund:
        return await self._repo.insert(data=data)
