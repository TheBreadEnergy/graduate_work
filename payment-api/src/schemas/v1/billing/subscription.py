import decimal
from uuid import UUID

from pydantic import BaseModel


class SubscriptionPaymentData(BaseModel):
    subscription_id: UUID
    account_id: UUID
    subscription_name: str
    price: decimal.Decimal
    currency: str
    payment_method: str | None
    wallet_id: UUID | None = None


class BatchSubscriptions(BaseModel):
    subscriptions: list[SubscriptionPaymentData]


class Subscription(BaseModel):
    subscription_id: UUID
    subscription_name: str
    price: decimal.Decimal
    currency: str
