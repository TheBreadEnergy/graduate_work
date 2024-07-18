from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWorkABC(ABC):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._rollback()

    async def commit(self) -> None:
        await self._commit()

    @abstractmethod
    async def _commit(self) -> None:
        ...

    @abstractmethod
    async def _rollback(self) -> None:
        ...


class SqlAlchemyUnitOfWork(UnitOfWorkABC):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self):
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self._session.close()

    async def _rollback(self) -> None:
        await self._session.rollback()

    async def _commit(self) -> None:
        await self._session.commit()
