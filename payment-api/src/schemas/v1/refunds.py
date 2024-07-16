from uuid import UUID

from pydantic import BaseModel
from src.models.domain.payment import PaymentStatus


class RefundStatusSchema(BaseModel):
    status: PaymentStatus
    payment_id: UUID
