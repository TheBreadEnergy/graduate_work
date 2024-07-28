import datetime
import decimal
from uuid import UUID

from src.models.domain.base import DomainBase
from src.models.domain.payment import PaymentStatus


class Refund(DomainBase):
    idempotency_key: str | None
    refund_id: UUID
    payment_id: UUID
    description: str | None
    money: decimal.Decimal
    status: PaymentStatus
    reason: str | None

    def __init__(
        self,
        account_id: UUID,
        payment_id: UUID,
        money: decimal.Decimal,
        status: PaymentStatus,
        reason: str | None = None,
        description: str | None = None,
        idempotency_key: str | None = None,
        created: datetime.datetime | None = None,
        id: UUID | None = None,
    ):
        super().__init__(id=id, account_id=account_id, created=created)
        self.money = money
        self.idempotency_key = idempotency_key
        self.payment_id = payment_id
        self.status = status
        self.reason = reason
        self.description = description
