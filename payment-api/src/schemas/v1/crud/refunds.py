import decimal
from uuid import UUID

from pydantic import BaseModel
from src.enums.payment import PaymentStatus


class RefundSchema(BaseModel):
    id: UUID
    account_id: UUID
    payment_id: UUID
    description: str
    money: decimal.Decimal
    status: PaymentStatus
    reason: str | None


class RefundCreateSchema(BaseModel):
    account_id: UUID
    payment_id: UUID
    description: str
    money: decimal.Decimal
    status: PaymentStatus
    reason: str | None
