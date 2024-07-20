from abc import ABC, abstractmethod
from uuid import UUID

import backoff
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.core.settings import BACKOFF_CONFIG
from src.database.models import wallets_table
from src.models.domain.wallet import Wallet
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.wallets import WalletCreateSchema


class WalletRepositoryABC(RepositoryABC, ABC):
    @abstractmethod
    async def get_for_user(self, *, account_id: UUID) -> Wallet | None:
        ...

    @abstractmethod
    async def delete(self, *, entity_id: UUID) -> None:
        ...


class WalletRepository(
    WalletRepositoryABC, SqlAlchemyRepository[Wallet, WalletCreateSchema]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Wallet, table=wallets_table)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def get_for_user(self, *, account_id: UUID) -> Wallet | None:
        query = select(Wallet).where(self._table.c.account_id == account_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def delete(self, *, entity_id: UUID) -> None:
        query = delete(Wallet).where(self._table.c.id == entity_id)
        await self._session.execute(query)


class CachedWalletRepository(WalletRepositoryABC):
    def __init__(self, repo: WalletRepositoryABC, cache: CacheClientABC):  # noqa
        self._repo = repo
        self._cache = cache
        self._key_entity_prefix = Wallet.__name__

    async def get(self, *, entity_id: UUID) -> Wallet | None:
        key = f"{self._key_entity_prefix}_{entity_id}"
        obj = await self._cache.get(key=key)
        if obj:
            return Wallet(**obj)
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity

    async def get_for_user(self, *, account_id: UUID) -> Wallet | None:
        key = f"{self._key_entity_prefix}_user_{account_id}"
        obj = await self._cache.get(key=key)
        if obj:
            return Wallet(**obj)
        entity = await self._repo.get_for_user(account_id=account_id)
        if not entity:
            return None
        await self._cache.insert(key=key, value=entity)
        return entity

    async def delete(self, *, entity_id: UUID) -> None:
        entity = await self._repo.get(entity_id=entity_id)
        if not entity:
            return
        account_key = f"{self._key_entity_prefix}_user_{entity.account_id}"
        key = f"{self._key_entity_prefix}_{entity_id}"
        await self._repo.delete(entity_id=entity_id)
        await self._cache.delete(account_key, key)

    async def gets(self, *, account_id: UUID | None = None) -> PaginatedPage[Wallet]:
        return await self._repo.gets(account_id=account_id)

    async def insert(self, *, data: WalletCreateSchema) -> Wallet:
        return await self._repo.insert(data=data)
