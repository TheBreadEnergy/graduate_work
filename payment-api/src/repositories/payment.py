from abc import abstractmethod
from uuid import UUID

import backoff
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.core.settings import BACKOFF_CONFIG
from src.database.models import payments_table
from src.enums.payment import PaymentStatus
from src.models.domain.payment import Payment
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.payments import PaymentCreateSchema


class PaymentRepositoryABC(RepositoryABC):
    """
    Интерфейс репозитория для пользовательских оплат.
    Нужен для спецификации базового интерфейса. Наследуется и расширяет интерфейс RepositoryABC добавляя методы
    payment_by_external_id, для получения оплат по внешнему идентификатору и filter_by_status для получения
    фильтрованного списка пользовательских оплат по статусу
    """

    @abstractmethod
    async def payment_by_external_id(self, *, payment_id: UUID) -> Payment | None:
        ...

    @abstractmethod
    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        ...


class PaymentRepository(
    PaymentRepositoryABC, SqlAlchemyRepository[Payment, PaymentCreateSchema]
):
    """
    Конкретная реализация интерфейса PaymentRepositoryABC.
    Реaлизация методов репозитория наследуется от конкретного  специфицированного шаблонного класса
    SqlAlchemyRepository, добавляя реализацию методов специфичных для PaymentRepositoryABC
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Payment, table=payments_table)

    async def payment_by_external_id(self, *, payment_id: UUID) -> Payment | None:
        query = select(self._model).where(self._table.c.payment_id == payment_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        query = select(self._model).where(self._table.c.status == status)
        return await paginate(self._session, query)


class CachedPaymentRepository(PaymentRepositoryABC):
    """
    Конкретная реализация интерфейса PaymentRepositoryABC с добавлением функциональности кеширования.
    Является декоратором над репозиторием реализующим PaymentRepositoryABC (PaymentRepository)
    """

    def __init__(self, repo: PaymentRepositoryABC, cache: CacheClientABC):  # noqa
        self._repo = repo
        self._cache = cache
        self._key_entity_prefix = Payment.__name__

    async def gets(self, *, account_id: UUID | None = None) -> PaginatedPage[Payment]:
        return await self._repo.gets(account_id=account_id)

    async def payment_by_external_id(self, *, payment_id: UUID) -> Payment | None:
        return await self._repo.payment_by_external_id(payment_id=payment_id)

    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        return await self._repo.filter_by_status(status=status)

    async def get(self, *, entity_id: UUID) -> Payment | None:
        key = f"{self._key_entity_prefix}_{entity_id}"
        obj = await self._cache.get(key=f"{self._key_entity_prefix}_{entity_id}")
        if obj:
            return Payment(**obj)
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity

    async def insert(self, *, data: PaymentCreateSchema) -> Payment:
        return await self._repo.insert(data=data)
