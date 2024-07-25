import datetime
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.exceptions.subscription import SubscriptionNotFoundException
from src.models.domain.subscription import Subscription
from src.repositories.subscriptions import SubscriptionsRepositoryABC
from src.schemas.v1.subscription import SubscriptionCreateSchema
from src.services.subscription import SubscriptionQueryService, SubscriptionService
from src.services.uow import UnitOfWorkABC


@pytest.mark.asyncio
async def test_get_subscriptions():
    mock_repository = AsyncMock()
    service = SubscriptionQueryService(repo=mock_repository)
    await service.get_subscriptions()
    mock_repository.gets.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_existing_subscription():
    id, created = uuid.uuid4(), datetime.datetime.now(datetime.timezone.utc)
    subscription = Subscription(
        name="test",
        description="test",
        code=1,
        tier=1,
        price=Decimal(500),
        currency="RUB",
        id=id,
        created=created,
    )
    mock_repo = MagicMock(spec=SubscriptionsRepositoryABC)
    mock_repo.get = AsyncMock(return_value=subscription)
    service = SubscriptionQueryService(repo=mock_repo)
    entity = await service.get_subscription(subscription_id=id)
    mock_repo.get.assert_awaited_once_with(entity_id=id)
    assert entity.name == subscription.name
    assert entity.code == subscription.code
    assert entity.price == subscription.price
    assert entity.currency == subscription.currency
    assert entity.id == subscription.id


@pytest.mark.asyncio
async def test_failure_get_subscription():
    id = uuid.uuid4()
    mock_repo = MagicMock(spec=SubscriptionsRepositoryABC)
    mock_repo.get = AsyncMock(return_value=None)
    service = SubscriptionQueryService(repo=mock_repo)
    with pytest.raises(SubscriptionNotFoundException):
        await service.get_subscription(subscription_id=id)
    mock_repo.get.assert_awaited_once_with(entity_id=id)


@pytest.mark.asyncio
async def test_create_subscription():
    subscription_data = MagicMock(spec=SubscriptionCreateSchema)
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    subscription_service = SubscriptionService(uow=uow)
    await subscription_service.create_subscription(subscription_data)
    uow.__aenter__.assert_called_once()
    uow.subscriptions.insert.assert_called_once_with(data=subscription_data)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_success_update_subscription():
    id, created = uuid.uuid4(), datetime.datetime.now(datetime.timezone.utc)
    subscription_data = SubscriptionCreateSchema(
        name="changed",
        description="changed",
        tier=2,
        code=2,
        price=Decimal(700),
        currency="RUB",
    )
    subscription = Subscription(
        name="test",
        description="test",
        code=1,
        tier=1,
        price=Decimal(500),
        currency="RUB",
        id=id,
        created=created,
    )
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    uow.subscriptions.get = AsyncMock(return_value=subscription)
    subscription_service = SubscriptionService(uow=uow)
    await subscription_service.update_subscription(
        subscription_id=id, subscription_data=subscription_data
    )
    uow.__aenter__.assert_called_once()
    uow.subscriptions.get.assert_awaited_once_with(entity_id=id)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_failure_update_subscription():
    id = uuid.uuid4()
    subscription_data = SubscriptionCreateSchema(
        name="changed",
        description="changed",
        tier=2,
        code=2,
        price=Decimal(700),
        currency="RUB",
    )
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    uow.subscriptions.get = AsyncMock(return_value=None)
    subscription_service = SubscriptionService(uow=uow)
    with pytest.raises(SubscriptionNotFoundException):
        await subscription_service.update_subscription(
            subscription_id=id, subscription_data=subscription_data
        )
    uow.__aenter__.assert_called_once()
    uow.subscriptions.get.assert_awaited_once_with(entity_id=id)
    uow.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_delete_subscription():
    id = uuid.uuid4()
    uow = MagicMock(spec=UnitOfWorkABC)
    uow.subscriptions = AsyncMock()
    subscription_service = SubscriptionService(uow=uow)
    await subscription_service.delete_subscription(subscription_id=id)
    uow.subscriptions.delete.assert_awaited_once_with(entity_id=id)
    uow.commit.assert_awaited_once()
