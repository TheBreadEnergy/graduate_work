from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.payment import PaymentRepository, PaymentRepositoryABC
from src.repositories.refunds import RefundRepository, RefundRepositoryABC
from src.repositories.wallet import WalletRepository, WalletRepositoryABC


class UnitOfWorkABC(ABC):
    payment_repository: PaymentRepositoryABC
    refund_repository: RefundRepositoryABC
    wallet_repository: WalletRepositoryABC

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
        self.payment_repository = PaymentRepository(session=self._session)
        self.refund_repository = RefundRepository(session=self._session)
        self.wallet_repository = WalletRepository(session=self._session)
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def _rollback(self) -> None:
        await self._session.rollback()

    async def _commit(self) -> None:
        await self._session.commit()
