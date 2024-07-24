from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.exceptions.subscription import SubscriptionNotFoundException
from src.models.domain.subscription import Subscription
from src.repositories.subscriptions import SubscriptionsRepositoryABC
from src.schemas.v1.subscription import SubscriptionCreateSchema
from src.services.uow import UnitOfWorkABC


class SubscriptionQueryServiceABC(ABC):
    @abstractmethod
    async def get_subscriptions(self) -> PaginatedPage[Subscription]:
        ...

    @abstractmethod
    async def get_subscription(self, subscription_id: UUID) -> Subscription:
        ...


class SubscriptionServiceABC(ABC):
    @abstractmethod
    async def create_subscription(
        self, subscription_data: SubscriptionCreateSchema
    ) -> Subscription:
        ...

    @abstractmethod
    async def update_subscription(
        self, subscription_id: UUID, subscription_data: SubscriptionCreateSchema
    ):
        ...

    @abstractmethod
    async def delete_subscription(self, subscription_id: UUID):
        ...


class SubscriptionQueryService(SubscriptionQueryServiceABC):
    def __init__(self, repo: SubscriptionsRepositoryABC):
        self._repo = repo

    async def get_subscriptions(self) -> PaginatedPage[Subscription]:
        return await self._repo.gets()

    async def get_subscription(self, subscription_id: UUID) -> Subscription:
        subscription = await self._repo.get(entity_id=subscription_id)
        if not subscription:
            raise SubscriptionNotFoundException()
        return subscription


class SubscriptionService(SubscriptionServiceABC):
    def __init__(self, uow: UnitOfWorkABC):
        self._uow = uow

    async def create_subscription(
        self, subscription_data: SubscriptionCreateSchema
    ) -> Subscription:
        async with self._uow:
            subscription = self._uow.subscriptions.insert(data=subscription_data)
            await self._uow.commit()
        return subscription

    async def update_subscription(
        self, subscription_id: UUID, subscription_data: SubscriptionCreateSchema
    ) -> Subscription:
        async with self._uow:
            subscription = await self._uow.subscriptions.get(entity_id=subscription_id)
            if not subscription:
                raise SubscriptionNotFoundException()
            subscription.price = subscription_data.price
            subscription.code = subscription_data.code
            subscription.currency = subscription_data.currency
            subscription.description = subscription_data.description
            subscription.name = subscription_data.name
            subscription.tier = subscription_data.tier
            await self._uow.commit()
        return subscription

    async def delete_subscription(self, subscription_id: UUID):
        async with self._uow:
            await self._uow.subscriptions.delete(entity_id=subscription_id)
            await self._uow.commit()
