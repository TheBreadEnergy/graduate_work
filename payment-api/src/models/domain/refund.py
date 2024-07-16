import decimal

from src.models.domain.base import DomainBase
from src.models.domain.payment import PaymentStatus


class Refund(DomainBase):
    description: str | None
    money: decimal
    status: PaymentStatus
    reason: str | None
