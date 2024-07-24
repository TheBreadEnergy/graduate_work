from functools import cache

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import RedisCacheClient
from src.cache.redis import get_cache
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.repositories.refunds import CachedRefundRepository, RefundRepository
from src.services.billing.payment_gateway import PaymentGatewayABC
from src.services.event_handler import EventHandlerABC
from src.services.refund import (
    RefundQueryService,
    RefundQueryServiceABC,
    RefundService,
    RefundServiceABC,
)
from src.services.uow import SqlAlchemyUnitOfWork


@add_factory_to_mapper(RefundQueryServiceABC)
@cache
def create_refund_query_service(
    session: AsyncSession = Depends(get_session),
    cache_client: Redis = Depends(get_cache),
) -> RefundQueryService:
    return RefundQueryService(
        refund_repository=CachedRefundRepository(
            repo=RefundRepository(session=session),
            cache=RedisCacheClient(redis_client=cache_client),
        )
    )


@add_factory_to_mapper(RefundServiceABC)
@cache
def create_refund_service(
    session: AsyncSession = Depends(get_session),
    payment_gateway: PaymentGatewayABC = Depends(),
    event_handler: EventHandlerABC = Depends(),
) -> RefundService:
    return RefundService(
        payment_gateway=payment_gateway,
        event_handler=event_handler,
        uow=SqlAlchemyUnitOfWork(session=session),
    )
