import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.exceptions.user_subscription import UserSubscriptionNotFoundException
from src.models.domain.subscription import Subscription
from src.models.domain.user_subscription import UserSubscription
from src.repositories.user_subscriptions import UserSubscriptionsRepositoryABC
from src.services.user_subscription import UserSubscriptionQueryService
from tests.testdata.subscription import SUBSCRIPTION

pytestmark = pytest.mark.asyncio


async def test_all_user_subscriptions():

    # Arrange
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act
    await service.get_all_user_subscriptions()

    # Assert
    mock_repository.get_filtered_subscriptions.assert_awaited_once_with(active=None)


async def test_all_active_user_subscriptions():

    # Arrange
    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)
    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act
    await service.get_all_user_subscriptions(active=True)

    # Assert
    mock_repository.get_filtered_subscriptions.assert_awaited_once_with(active=True)


async def test_user_subscriptions():

    # Arrange
    user_id = uuid.uuid4()

    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)

    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act
    await service.get_user_subscriptions(account_id=user_id)

    # Assert
    mock_repository.get_user_subscriptions.assert_awaited_once_with(
        user_id=user_id, active=None
    )


async def test_active_user_subscriptions():
    # Arrange
    user_id = uuid.uuid4()

    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)

    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act
    await service.get_user_subscriptions(account_id=user_id, active=True)

    # Assert
    mock_repository.get_user_subscriptions.assert_awaited_once_with(
        user_id=user_id, active=True
    )


@pytest.mark.parametrize("subscription", [SUBSCRIPTION])
async def test_success_subscription(subscription: Subscription):

    # Arrange
    user_subscription = UserSubscription(
        id=subscription.id,
        user_id=subscription.id,
        subscription=subscription,
        price=Decimal(100),
        currency="RUB",
        promo_id=subscription.id,
        active=True,
    )

    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)

    mock_repository.get = AsyncMock(return_value=user_subscription)

    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act
    await service.get_subscription(subscription_id=subscription.id)

    # Assert
    mock_repository.get.assert_awaited_once_with(entity_id=subscription.id)


async def test_failure_subscription():

    # Arrange
    id = uuid.uuid4()

    mock_repository = MagicMock(spec=UserSubscriptionsRepositoryABC)

    mock_repository.get = AsyncMock(return_value=None)

    service = UserSubscriptionQueryService(repo=mock_repository)

    # Act + Assert
    with pytest.raises(UserSubscriptionNotFoundException):
        await service.get_subscription(subscription_id=id)

    mock_repository.get.assert_awaited_once_with(entity_id=id)
