from uuid import UUID

from src.models.domain.base import DomainBase


class Wallet(DomainBase):
    payment_method_id: UUID
    title: str
    reccurent_payment: bool
