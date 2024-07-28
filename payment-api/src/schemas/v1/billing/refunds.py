from uuid import UUID

from pydantic import BaseModel
from src.models.domain.payment import PaymentStatus


class RefundStatusSchema(BaseModel):
    refund_id: UUID
    reason: str | None = None
    status: PaymentStatus
    payment_id: UUID
