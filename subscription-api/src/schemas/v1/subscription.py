import datetime
import decimal
from uuid import UUID

from pydantic import BaseModel


class SubscriptionSchema(BaseModel):
    id: UUID
    name: str
    description: str | None
    tier: int
    code: int
    price: decimal.Decimal
    currency: str
    created: datetime.datetime


class SubscriptionCreateSchema(BaseModel):
    name: str
    description: str | None
    tier: int
    code: int
    price: decimal.Decimal
    currency: str
