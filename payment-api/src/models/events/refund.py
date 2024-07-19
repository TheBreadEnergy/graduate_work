import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RefundEventABC(BaseModel):
    refund_id: UUID
    created_at: datetime.datetime = Field(
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class RefundCreatedEvent(RefundEventABC):
    user_id: UUID


class RefundCancelledEvent(RefundEventABC):
    reason: str


class RefundSuccessEvent(RefundEventABC):
    ...
