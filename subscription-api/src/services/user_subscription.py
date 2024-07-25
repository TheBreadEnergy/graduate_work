from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.exceptions.user_subscription import UserSubscriptionNotFoundException
from src.models.domain.user_subscription import UserSubscription
from src.repositories.user_subscriptions import UserSubscriptionsRepositoryABC


class UserSubscriptionQueryServiceABC(ABC):
    @abstractmethod
    async def get_subscription(self, subscription_id: UUID) -> UserSubscription:
        ...

    @abstractmethod
    async def get_all_user_subscriptions(
        self, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        ...

    @abstractmethod
    async def get_user_subscriptions(
        self, account_id: UUID, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        ...


class UserSubscriptionQueryService(UserSubscriptionQueryServiceABC):
    def __init__(self, repo: UserSubscriptionsRepositoryABC):
        self._repo = repo

    async def get_subscription(self, subscription_id: UUID) -> UserSubscription:
        user_subscription = await self._repo.get(entity_id=subscription_id)
        if not user_subscription:
            raise UserSubscriptionNotFoundException()
        return user_subscription

    async def get_all_user_subscriptions(
        self, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        return await self._repo.get_filtered_subscriptions(active=active)

    async def get_user_subscriptions(
        self, account_id: UUID, active: bool | None = None
    ) -> PaginatedPage[UserSubscription]:
        return await self._repo.get_user_subscriptions(
            user_id=account_id, active=active
        )
