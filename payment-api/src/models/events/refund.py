import datetime
from uuid import UUID

from pydantic import BaseModel


class RefundEventABC(BaseModel):
    refund_id: UUID
    payment_id: UUID
    user_id: UUID
    created_at: datetime.datetime


class RefundCreatedEvent(RefundEventABC):
    ...


class RefundCancelledEvent(RefundEventABC):
    reason: str


class RefundSuccessEvent(RefundEventABC):
    ...
