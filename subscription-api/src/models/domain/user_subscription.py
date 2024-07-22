import datetime
import decimal
from uuid import UUID

from src.models.domain.base import DomainBase
from src.models.domain.subscription import Subscription


# TODO: Вынести логику парсинга в отдельный метод
class UserSubscription(DomainBase):
    user_id: UUID
    subscription: Subscription
    price: decimal.Decimal
    currency: str
    promo_id: UUID | None
    active: bool
    last_notified: datetime.datetime
    last_payed: datetime.datetime

    def __init__(
        self,
        user_id: UUID,
        subscription: Subscription | dict,
        price: decimal.Decimal,
        currency: str,
        promo_id: UUID | None,
        active: bool,
        last_notified: datetime.datetime | None = None,
        last_payed: datetime.datetime | None = None,
        id: UUID | None = None,
        created: datetime.datetime | None = None,
    ):
        super().__init__(id=id, created=created)
        self.user_id = user_id
        if isinstance(subscription, dict):
            self.subscription = Subscription(**subscription)
        else:
            self.subscription = subscription
        self.price = price
        self.currency = currency
        self.promo_id = promo_id
        self.active = active
        self.last_payed = last_payed
        self.last_notified = last_notified
