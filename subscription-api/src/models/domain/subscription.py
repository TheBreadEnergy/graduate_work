import datetime
import decimal
from uuid import UUID

from src.models.domain.base import DomainBase

# TODO: Вынести логику парсинга в отдельный метод


class Subscription(DomainBase):
    name: str
    description: str | None
    tier: int
    code: int
    price: decimal.Decimal
    currency: str

    def __init__(
        self,
        name: str,
        description: str | None,
        tier: int,
        code: int,
        price: decimal.Decimal,
        currency: str,
        id: UUID | None = None,
        created: datetime.datetime | None = None,
    ):
        super().__init__(id=id, created=created)
        self.name = name
        self.description = description
        self.tier = tier
        self.code = code
        self.price = price
        self.currency = currency
