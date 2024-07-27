from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

import backoff
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.cache.cache_client import CacheClientABC
from src.core.pagination import PaginatedPage
from src.core.settings import BACKOFF_CONFIG
from src.database.models import wallets_table
from src.models.domain.wallet import Wallet
from src.repositories.base import RepositoryABC, SqlAlchemyRepository
from src.schemas.v1.crud.wallets import WalletCreateSchema


class WalletRepositoryABC(RepositoryABC, ABC):
    """
    Интерфейс репозитория для пользовательских способов оплаты.
    Нужен для спецификации базового интерфейса. Наследуется и расширяет интерфейс RepositoryABC добавляя методы
    get_for_user, для получения способов оплаты для пользователя и delete для удаления выбранного способа оплаты
    """

    @abstractmethod
    async def get_for_user(self, *, account_id: UUID) -> list[Wallet]:
        ...

    @abstractmethod
    async def delete(self, *, entity_id: UUID) -> None:
        ...


class WalletRepository(
    WalletRepositoryABC, SqlAlchemyRepository[Wallet, WalletCreateSchema]
):
    """
    Конкретная реализация интерфейса WalletRepositoryABC.
    Реaлизация методов репозитория наследуется от конкретного  специфицированного шаблонного класса
    SqlAlchemyRepository, добавляя реализацию методов специфичных для WalletRepositoryABC
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Wallet, table=wallets_table)

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def get_for_user(self, *, account_id: UUID) -> Sequence[Wallet]:
        query = select(Wallet).where(self._table.c.account_id == account_id)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def insert(self, *, data: WalletCreateSchema) -> Wallet:
        query = select(Wallet).where(
            and_(
                self._table.c.account_id == data.account_id,
                self._table.c.payment_method_id == data.payment_method_id,
            )
        )
        result = await self._session.execute(query)
        wallet = result.scalar_one_or_none()
        if not wallet:
            return super().insert(data=data)
        return wallet

    @backoff.on_exception(**BACKOFF_CONFIG)
    async def delete(self, *, entity_id: UUID) -> None:
        query = delete(Wallet).where(self._table.c.id == entity_id)
        await self._session.execute(query)


class CachedWalletRepository(WalletRepositoryABC):
    """
    Конкретная реализация интерфейса WalletRepositoryABC с добавлением функциональности кеширования.
    Является декоратором над репозиторием реализующим WalletRepositoryABC (WalletRepository)
    """

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

    async def get_for_user(self, *, account_id: UUID) -> list[Wallet]:
        return await self._repo.get_for_user(account_id=account_id)

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
