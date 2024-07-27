from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar
from uuid import UUID

import backoff
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Table, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.pagination import PaginatedPage
from src.core.settings import BACKOFF_CONFIG
from src.models.domain.base import DomainBase

ModelType = TypeVar("ModelType", bound=DomainBase)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)


class RepositoryABC(ABC):
    """
    Базовый интерфейс для репозиториев.
    Здесь перечислены базовые операции которые должны реализовывать все репозитории
    """

    @abstractmethod
    def gets(self, *args, **kwargs):
        ...

    @abstractmethod
    def get(self, *args, **kwargs):
        ...

    @abstractmethod
    def insert(self, *args, **kwargs):
        ...

    @abstractmethod
    def delete(self, *args, **kwargs):
        ...


class SqlAlchemyRepository(RepositoryABC, Generic[ModelType, CreateModelType]):
    """
    Конретная реализация интерфейса RepositoryABC для ORM sqlalchemy.
    Определяет реализации методов по умолчанию
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType], table: Table):
        self._session = session
        self._model = model
        self._table = table

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def gets(self) -> PaginatedPage[ModelType]:
        query = select(self._model)
        return await paginate(self._session, query)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def get(self, *, entity_id: UUID) -> ModelType | None:
        query = select(self._model).where(self._table.c.id == entity_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    @backoff.on_exception(**BACKOFF_CONFIG)
    def insert(self, *, data: CreateModelType) -> ModelType:
        jsonable_data = data.model_dump()
        obj = self._model(**jsonable_data)
        self._session.add(obj)
        return obj

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def delete(self, *, entity_id: UUID):
        query = delete(self._model).where(self._table.c.id == entity_id)
        await self._session.execute(query)
