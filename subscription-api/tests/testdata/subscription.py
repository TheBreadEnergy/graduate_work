import datetime
import uuid
from decimal import Decimal

from src.models.domain.subscription import Subscription
from src.schemas.v1.subscription import SubscriptionCreateSchema


def generate_subscription():
    id, created = uuid.uuid4(), datetime.datetime.now(datetime.timezone.utc)
    return Subscription(
        name="test",
        description="test",
        code=1,
        tier=1,
        price=Decimal(500),
        currency="RUB",
        id=id,
        created=created,
    )


def generate_change_subscription():
    return SubscriptionCreateSchema(
        name="changed",
        description="changed",
        tier=1,
        code=1,
        price=Decimal(700),
        currency="RUB",
    )


SUBSCRIPTION = generate_subscription()


CHANGE_SUBSCRIPTION = generate_change_subscription()
