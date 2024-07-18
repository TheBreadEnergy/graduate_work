import decimal
from uuid import UUID

from src.models.domain.base import DomainBase
from src.models.domain.payment import PaymentStatus


class Refund(DomainBase):
    idempotency_key: str | None
    payment_id: UUID
    description: str | None
    money: decimal
    status: PaymentStatus
    reason: str | None
