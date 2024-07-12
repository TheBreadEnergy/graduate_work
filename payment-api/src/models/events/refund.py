import datetime
from uuid import UUID

from pydantic import BaseModel


class RefundEventABC(BaseModel):
    refund_id: UUID
    created_at: datetime.datetime


class RefundCreatedEvent(RefundEventABC):
    user_id: UUID


class RefundCancelledEvent(RefundEventABC):
    reason: str


class RefundSuccessEvent(RefundEventABC):
    ...
