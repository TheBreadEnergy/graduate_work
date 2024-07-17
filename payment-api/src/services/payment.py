from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.models.domain.payment import Payment


class PaymentQueryServiceABC(ABC):
    @abstractmethod
    async def get_payments(
        self, account_id: UUID | None = None
    ) -> PaginatedPage[Payment]:
        ...

    @abstractmethod
    async def get_payment(self, payment_id: UUID) -> Payment:
        ...


class PaymentCommandServiceABC(ABC):
    @abstractmethod
    async def make_payment(self, subscription_id: UUID):
        ...
