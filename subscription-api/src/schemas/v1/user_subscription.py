import datetime
import decimal
from uuid import UUID

from pydantic import BaseModel
from src.schemas.v1.subscription import SubscriptionSchema


class UserSubscriptionSchema(BaseModel):
    id: UUID
    subscription: SubscriptionSchema
    price: decimal.Decimal
    currency: str
    promo_id: UUID
    active: bool
    last_payed: datetime.datetime
    created: datetime.datetime


class UserSubscriptionCreateSchema(BaseModel):
    subscription: SubscriptionSchema
    price: decimal.Decimal
    currency: str
    promo_id: UUID
    active: bool
