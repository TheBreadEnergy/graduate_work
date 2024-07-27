import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.exceptions.subscription import SubscriptionNotFoundException
from src.models.domain.subscription import Subscription
from src.repositories.subscriptions import SubscriptionsRepositoryABC
from src.schemas.v1.subscription import SubscriptionCreateSchema
from src.services.subscription import SubscriptionQueryService, SubscriptionService
from src.services.uow import UnitOfWorkABC
from tests.testdata.subscription import CHANGE_SUBSCRIPTION, SUBSCRIPTION

pytestmark = pytest.mark.asyncio


async def test_get_subscriptions():
    mock_repository = AsyncMock()
    service = SubscriptionQueryService(repo=mock_repository)
    await service.get_subscriptions()
    mock_repository.gets.assert_awaited_once()


@pytest.mark.parametrize("subscription", [SUBSCRIPTION])
async def test_get_existing_subscription(subscription: Subscription):

    # Arrange
    mock_repo = MagicMock(spec=SubscriptionsRepositoryABC)
    mock_repo.get = AsyncMock(return_value=subscription)
    service = SubscriptionQueryService(repo=mock_repo)

    # Act
    await service.get_subscription(subscription_id=subscription.id)

    # Assert
    mock_repo.get.assert_awaited_once_with(entity_id=subscription.id)


async def test_failure_get_subscription():
    # Arrange
    id = uuid.uuid4()
    mock_repo = MagicMock(spec=SubscriptionsRepositoryABC)
    mock_repo.get = AsyncMock(return_value=None)
    service = SubscriptionQueryService(repo=mock_repo)

    # Act + Assert
    with pytest.raises(SubscriptionNotFoundException):
        await service.get_subscription(subscription_id=id)

    mock_repo.get.assert_awaited_once_with(entity_id=id)


async def test_create_subscription():

    # Arrange
    subscription_data = MagicMock(spec=SubscriptionCreateSchema)
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    subscription_service = SubscriptionService(uow=uow)

    # Act
    await subscription_service.create_subscription(subscription_data)

    # Assert
    uow.__aenter__.assert_called_once()
    uow.subscriptions.insert.assert_called_once_with(data=subscription_data)
    uow.commit.assert_awaited_once()


@pytest.mark.parametrize("update_data", [CHANGE_SUBSCRIPTION])
@pytest.mark.parametrize("subscription", [SUBSCRIPTION])
async def test_success_update_subscription(
    update_data: SubscriptionCreateSchema, subscription: Subscription
):
    # Arrange
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    uow.subscriptions.get = AsyncMock(return_value=subscription)
    subscription_service = SubscriptionService(uow=uow)

    # Act
    await subscription_service.update_subscription(
        subscription_id=subscription.id, subscription_data=update_data
    )

    # Assert
    uow.__aenter__.assert_called_once()
    uow.subscriptions.get.assert_awaited_once_with(entity_id=subscription.id)
    uow.commit.assert_awaited_once()


@pytest.mark.parametrize("update_data", [CHANGE_SUBSCRIPTION])
async def test_failure_update_subscription(update_data: SubscriptionCreateSchema):
    # Arrange
    id = uuid.uuid4()

    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    uow.subscriptions.get = AsyncMock(return_value=None)

    subscription_service = SubscriptionService(uow=uow)

    # Act + Assert
    with pytest.raises(SubscriptionNotFoundException):
        await subscription_service.update_subscription(
            subscription_id=id, subscription_data=update_data
        )
    uow.__aenter__.assert_called_once()
    uow.subscriptions.get.assert_awaited_once_with(entity_id=id)
    uow.__aexit__.assert_called_once()


async def test_delete_subscription():

    # Arrange
    id = uuid.uuid4()
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    subscription_service = SubscriptionService(uow=uow)

    # Act
    await subscription_service.delete_subscription(subscription_id=id)

    # Assert
    uow.subscriptions.delete.assert_awaited_once_with(entity_id=id)
    uow.commit.assert_awaited_once()
