import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentEventABC(BaseModel):
    payment_id: UUID
    created_at: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc)
    )


class PaymentCreatedEvent(PaymentEventABC):
    user_id: UUID
    license_id: UUID


class PaymentCancelledEvent(PaymentEventABC):
    reason: str


class PaymentSuccessEvent(PaymentEventABC):
    ...
