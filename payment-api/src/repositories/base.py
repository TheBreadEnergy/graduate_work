from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.pagination import PaginatedPage
from src.models.domain.base import DomainBase

ModelType = TypeVar("ModelType", bound=DomainBase)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)


class RepositoryABC(ABC):
    @abstractmethod
    def gets(self, *args, **kwargs):
        ...

    @abstractmethod
    def get(self, *args, **kwargs):
        ...

    @abstractmethod
    def insert(self, *args, **kwargs):
        ...


class SqlAlchemyRepository(RepositoryABC, Generic[ModelType, CreateModelType]):
    def __init__(
        self, session: AsyncSession, model_type: Type[ModelType], table: Table
    ):
        self._session = session
        self._model = model_type
        self._table = table

    async def gets(self, *, account_id: UUID | None = None) -> PaginatedPage[ModelType]:
        query = select(ModelType)
        if account_id:
            query = query.where(self._table.c.account_id == account_id)
        return await paginate(self._session, query)

    async def get(self, *, entity_id: UUID) -> ModelType | None:
        query = select(ModelType).where(self._table.c.id == entity_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    def insert(self, *, data: CreateModelType) -> ModelType:
        jsonable_data = data.model_dump()
        obj = self._model(**jsonable_data)
        self._session.add(obj)
        return obj
