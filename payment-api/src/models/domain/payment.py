import datetime
import decimal
from uuid import UUID

from src.enums.payment import PaymentStatus
from src.models.domain.base import DomainBase


class Payment(DomainBase):
    idempotency_key: str | None
    payment_id: UUID
    description: str | None
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None

    def __init__(
        self,
        account_id: UUID,
        subscription_id: UUID,
        payment_id: UUID,
        price: decimal.Decimal,
        currency: str,
        status: PaymentStatus,
        idempotency_key: str | None = None,
        description: str | None = None,
        reason: str | None = None,
        created: datetime.datetime | None = None,
        id: UUID | None = None,
    ):
        super().__init__(id=id, account_id=account_id, created=created)
        self.subscription_id = subscription_id
        self.payment_id = payment_id
        self.price = price
        self.currency = currency
        self.status = status
        self.idempotency_key = idempotency_key
        self.description = description
        self.reason = reason
