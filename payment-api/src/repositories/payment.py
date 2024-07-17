from abc import abstractmethod
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.database.models import payments_table
from src.enums.payment import PaymentStatus
from src.models.domain.payment import Payment
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.payments import PaymentCreateSchema


class PaymentRepositoryABC(RepositoryABC):
    @abstractmethod
    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        ...


class PaymentRepository(
    PaymentRepositoryABC, SqlAlchemyRepository[Payment, PaymentCreateSchema]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model_type=Payment, table=payments_table)

    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        query = select(self._model).where(self._table.c.status == status)
        return await paginate(self._session, query)


class CachedPaymentRepository(
    PaymentRepositoryABC, SqlAlchemyRepository[Payment, PaymentCreateSchema]
):
    async def filter_by_status(
        self, *, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        return await self._repo.filter_by_status(status=status)

    def __init__(self, repo: PaymentRepositoryABC, cache: CacheClientABC):  # noqa
        self._repo = repo
        self._cache = cache
        self._key_entity_prefix = Payment.__name__

    async def get(self, *, entity_id: UUID) -> Payment | None:
        key = f"{self._key_entity_prefix}_{entity_id}"
        obj = await self._cache.get(key=f"{self._key_entity_prefix}_{entity_id}")
        if obj:
            return self._model.model_validate(obj)
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity
