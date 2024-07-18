from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.enums.payment import PaymentStatus
from src.models.domain.refund import Refund
from src.repositories.refunds import RefundRepositoryABC


class RefundQueryServiceABC(ABC):
    @abstractmethod
    async def gets(self, *, account_id: UUID) -> PaginatedPage[Refund]:
        ...

    @abstractmethod
    async def get(self, *, refund_id: UUID) -> Refund:
        ...


class RefundQueryService(RefundQueryServiceABC):
    def __init__(self, refund_repository: RefundRepositoryABC):
        self._refund_repository = refund_repository

    async def gets(self, *, account_id: UUID) -> PaginatedPage[Refund]:
        return await self._refund_repository.gets(account_id=account_id)

    async def get(self, *, refund_id: UUID) -> Refund:
        return await self._refund_repository.get(entity_id=refund_id)

    async def filter_by_status(self, status: PaymentStatus) -> PaginatedPage[Refund]:
        return await self._refund_repository.filter_by_status(status=status)


class RefundServiceABC(ABC):
    @abstractmethod
    async def refund(self, payment_id: UUID) -> Refund:
        ...
