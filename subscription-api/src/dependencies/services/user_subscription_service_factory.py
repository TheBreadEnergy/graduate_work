from functools import cache

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import RedisCacheClient
from src.cache.redis import get_cache
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.repositories.user_subscriptions import (
    CachedUserSubscriptionsRepository,
    UserSubscriptionsRepository,
)
from src.services.user_subscription import (
    UserSubscriptionQueryService,
    UserSubscriptionQueryServiceABC,
)


@add_factory_to_mapper(UserSubscriptionQueryServiceABC)
@cache
def create_user_subscription_service(
    session: AsyncSession = Depends(get_session),
    cache_client: Redis = Depends(get_cache),
) -> UserSubscriptionQueryService:
    return UserSubscriptionQueryService(
        repo=CachedUserSubscriptionsRepository(
            repo=UserSubscriptionsRepository(session=session),
            cache=RedisCacheClient(redis_client=cache_client),
        )
    )
