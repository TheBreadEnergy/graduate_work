import datetime
from uuid import UUID

from src.models.domain.base import DomainBase


class Wallet(DomainBase):
    payment_method_id: UUID
    title: str
    reccurent_payment: bool

    def __init__(
        self,
        payment_method_id: UUID,
        title: str,
        reccurent_payment: bool,
        account_id: UUID,
        id: UUID | None = None,
        created: datetime.datetime | None = None,
    ):

        super().__init__(id=id, account_id=account_id, created=created)
        self.payment_method_id = payment_method_id
        self.title = title
        self.reccurent_payment = reccurent_payment
