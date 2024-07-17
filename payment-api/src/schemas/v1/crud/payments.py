import datetime
import decimal
from uuid import UUID

from pydantic import BaseModel
from src.models.domain.payment import PaymentStatus


class PaymentSchema(BaseModel):
    id: UUID
    account_id: UUID
    description: str | None
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None
    created_at: datetime.datetime


class PaymentCreateSchema(BaseModel):
    account_id: UUID
    description: str | None
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None
