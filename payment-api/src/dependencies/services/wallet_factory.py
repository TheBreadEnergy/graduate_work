from functools import cache

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import RedisCacheClient
from src.cache.redis import get_cache
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.repositories.wallet import CachedWalletRepository, WalletRepository
from src.services.uow import SqlAlchemyUnitOfWork
from src.services.wallet import (
    WalletQueryService,
    WalletQueryServiceABC,
    WalletService,
    WalletServiceABC,
)


@add_factory_to_mapper(WalletQueryServiceABC)
@cache
def create_wallet_query_service(
    session: AsyncSession = Depends(get_session),
    cache_client: Redis = Depends(get_cache),
) -> WalletQueryService:
    return WalletQueryService(
        wallet_repository=CachedWalletRepository(
            repo=WalletRepository(session=session),
            cache=RedisCacheClient(redis_client=cache_client),
        ),
    )


@add_factory_to_mapper(WalletServiceABC)
@cache
def create_wallet_service(
    session: AsyncSession = Depends(get_session),
) -> WalletService:
    return WalletService(uow=SqlAlchemyUnitOfWork(session=session))
