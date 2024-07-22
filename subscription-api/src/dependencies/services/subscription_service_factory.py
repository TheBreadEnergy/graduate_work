from functools import cache

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import RedisCacheClient
from src.cache.redis import get_cache
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.repositories.subscriptions import (
    CachedSubscriptionsRepository,
    SubscriptionsRepository,
)
from src.services.subscription import (
    SubscriptionQueryService,
    SubscriptionQueryServiceABC,
    SubscriptionService,
    SubscriptionServiceABC,
)
from src.services.uow import SqlAlchemyUnitOfWork


@add_factory_to_mapper(SubscriptionQueryServiceABC)
@cache
def create_subscription_query_service(
    session: AsyncSession = Depends(get_session),
    cache_client: Redis = Depends(get_cache),
) -> SubscriptionQueryService:
    return SubscriptionQueryService(
        repo=CachedSubscriptionsRepository(
            repo=SubscriptionsRepository(session=session),
            cache=RedisCacheClient(redis_client=cache_client),
        )
    )


@add_factory_to_mapper(SubscriptionServiceABC)
@cache
def create_subscription_service(
    session: AsyncSession = Depends(get_session),
) -> SubscriptionService:
    return SubscriptionService(uow=SqlAlchemyUnitOfWork(session=session))
