import datetime
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.exceptions.user_subscription import UserSubscriptionNotFoundException
from src.models.domain.subscription import Subscription
from src.models.domain.user_subscription import UserSubscription
from src.repositories.user_subscriptions import UserSubscriptionsRepositoryABC
from src.services.user_subscription import UserSubscriptionQueryService


@pytest.mark.asyncio
async def test_all_user_subscriptions():
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)
    await service.get_all_user_subscriptions()
    mock_repository.get_filtered_subscriptions.assert_awaited_once_with(active=None)


@pytest.mark.asyncio
async def test_all_active_user_subscriptions():
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)
    await service.get_all_user_subscriptions(active=True)
    mock_repository.get_filtered_subscriptions.assert_awaited_once_with(active=True)


@pytest.mark.asyncio
async def test_user_subscriptions():
    user_id = uuid.uuid4()
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)
    await service.get_user_subscriptions(account_id=user_id)
    mock_repository.get_user_subscriptions.assert_awaited_once_with(
        user_id=user_id, active=None
    )


@pytest.mark.asyncio
async def test_active_user_subscriptions():
    user_id = uuid.uuid4()
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)
    await service.get_user_subscriptions(account_id=user_id, active=True)
    mock_repository.get_user_subscriptions.assert_awaited_once_with(
        user_id=user_id, active=True
    )


@pytest.mark.asyncio
async def test_success_subscription():
    id = uuid.uuid4()
    subscription = Subscription(
        name="test",
        description="test",
        code=1,
        tier=1,
        price=Decimal(500),
        currency="RUB",
        id=id,
        created=datetime.datetime.now(datetime.timezone.utc),
    )
    user_subscription = UserSubscription(
        id=id,
        user_id=id,
        subscription=subscription,
        price=Decimal(100),
        currency="RUB",
        promo_id=id,
        active=True,
    )
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    mock_repository.get = AsyncMock(return_value=user_subscription)
    service = UserSubscriptionQueryService(repo=mock_repository)
    await service.get_subscription(subscription_id=id)
    mock_repository.get.assert_awaited_once_with(entity_id=id)


@pytest.mark.asyncio
async def test_failure_subscription():
    id = uuid.uuid4()
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    mock_repository.get = AsyncMock(return_value=None)
    service = UserSubscriptionQueryService(repo=mock_repository)
    with pytest.raises(UserSubscriptionNotFoundException):
        await service.get_subscription(subscription_id=id)
    mock_repository.get.assert_awaited_once_with(entity_id=id)
