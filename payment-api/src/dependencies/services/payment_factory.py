from functools import cache

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import RedisCacheClient
from src.cache.redis import get_cache
from src.core.settings import settings
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.repositories.payment import CachedPaymentRepository, PaymentRepository
from src.services.billing.payment_gateway import (
    MockPaymentGateway,
    PaymentGatewayABC,
    YooKassaPaymentGateway,
)
from src.services.event_handler import EventHandlerABC
from src.services.payment import (
    PaymentQueryService,
    PaymentQueryServiceABC,
    PaymentService,
    PaymentServiceABC,
)
from src.services.uow import SqlAlchemyUnitOfWork


@add_factory_to_mapper(PaymentGatewayABC)
@cache
def create_payment_gateway() -> YooKassaPaymentGateway | MockPaymentGateway:
    return YooKassaPaymentGateway() if not settings.debug else MockPaymentGateway()


@add_factory_to_mapper(PaymentQueryServiceABC)
@cache
def create_payment_query_service(
    session: AsyncSession = Depends(get_session),
    cache_client: Redis = Depends(get_cache),
) -> PaymentQueryService:
    return PaymentQueryService(
        payment_repository=CachedPaymentRepository(
            repo=PaymentRepository(session=session),
            cache=RedisCacheClient(redis_client=cache_client),
        )
    )


@add_factory_to_mapper(PaymentServiceABC)
@cache
def create_payment_service(
    session: AsyncSession = Depends(get_session),
    payment_gateway: PaymentGatewayABC = Depends(),
    event_handler: EventHandlerABC = Depends(),
) -> PaymentService:
    return PaymentService(
        payment_gateway=payment_gateway,
        event_hander=event_handler,
        uow=SqlAlchemyUnitOfWork(session=session),
    )
