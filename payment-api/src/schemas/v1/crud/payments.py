import datetime
import decimal
from uuid import UUID

from pydantic import BaseModel
from src.models.domain.payment import PaymentStatus
from src.schemas.v1.crud.enums import Currency, PaymentMethod


class PaymentSchema(BaseModel):
    id: UUID
    account_id: UUID
    description: str | None
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None
    created: datetime.datetime


class PaymentCreateSchema(BaseModel):
    account_id: UUID
    description: str | None
    payment_id: UUID
    subscription_id: UUID
    price: decimal.Decimal
    currency: str
    status: PaymentStatus
    reason: str | None


class PaymentOperationSchema(BaseModel):
    subscription_id: UUID
    subscription_name: str
    price: decimal.Decimal
    currency: Currency
    save_payment_method: bool
    payment_method: PaymentMethod


class PaymentStatusSchema(BaseModel):
    status: PaymentStatus
    redirection_url: str
