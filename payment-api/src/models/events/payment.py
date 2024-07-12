import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentEventABC(BaseModel):
    payment_id: UUID
    user_id: UUID
    license_id: UUID
    created_at: datetime.datetime


class PaymentCreatedEvent(PaymentEventABC):
    ...


class PaymentCanceledEvent(PaymentEventABC):
    reason: str


class PaymentSuccessEvent(PaymentEventABC):
    ...
