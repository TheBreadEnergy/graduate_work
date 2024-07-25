import datetime
from uuid import UUID

from pydantic import BaseModel


class PaymentEventABC(BaseModel):
    payment_id: UUID
    created_at: datetime.datetime


class PaymentCancelledEvent(PaymentEventABC):
    reason: str


class PaymentSuccessEvent(PaymentEventABC): ...
