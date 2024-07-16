import decimal
from enum import Enum
from uuid import UUID

from src.models.domain.base import DomainBase


class PaymentStatus(Enum):
    created = "created"
    pending = "pending"
    success = "succeeded"
    cancelled = "cancelled"
    waiting_to_capture = "waiting_for_capture"


class Payment(DomainBase):
    account_id: UUID
    idempotency_key: UUID | None
    description: str | None
    subscription_id: UUID
    price: decimal
    currency: str
    status: PaymentStatus
    reason: str | None
