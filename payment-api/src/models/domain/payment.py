import decimal
from uuid import UUID

from src.enums.payment import PaymentStatus
from src.models.domain.base import DomainBase


class Payment(DomainBase):
    idempotency_key: str | None
    description: str | None
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None
