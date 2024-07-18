from abc import abstractmethod
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.database.models import refunds_table
from src.enums.payment import PaymentStatus
from src.models.domain.refund import Refund
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.refunds import RefundCreateSchema


class RefundRepositoryABC(RepositoryABC):
    @abstractmethod
    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        ...


class RefundRepository(
    RefundRepositoryABC, SqlAlchemyRepository[Refund, RefundCreateSchema]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Refund, table=refunds_table)

    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        query = select(Refund).where(self._table.c.status == status)
        return await paginate(self._session, query)


class CachedRefundRepository(
    RefundRepositoryABC, SqlAlchemyRepository[Refund, RefundCreateSchema]
):
    def __init__(self, repo: RefundRepository, cache: CacheClientABC):  # noqa
        self._repo = repo
        self._cache = cache
        self._key_entity_prefix = Refund.__name__

    async def filter_by_status(self, *, status: PaymentStatus) -> PaginatedPage[Refund]:
        return await self._repo.filter_by_status(status=status)

    async def get(self, *, entity_id: UUID) -> Refund | None:
        key = f"{self._key_entity_prefix}_{entity_id}"
        obj = await self._cache.get(key=key)
        if obj:
            return self._model.model_validate(obj)
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity
