from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from src.exceptions.wallet import WalletNotFoundException
from src.models.domain.wallet import Wallet
from src.repositories.wallet import WalletRepositoryABC
from src.services.uow import UnitOfWorkABC


class WalletQueryServiceABC(ABC):
    @abstractmethod
    async def get_wallet(self, *, account_id: UUID) -> Sequence[Wallet]:
        ...


class WalletQueryService(WalletQueryServiceABC):
    def __init__(self, wallet_repository: WalletRepositoryABC):
        self._repo = wallet_repository

    async def get_wallet(self, *, account_id: UUID) -> Sequence[Wallet]:
        wallets = await self._repo.get_for_user(account_id=account_id)
        return wallets


class WalletServiceABC(ABC):
    @abstractmethod
    async def make_wallet_preffered(
        self, *, wallet_id: UUID, account_id: UUID, preferred: bool
    ) -> Wallet:
        ...


class WalletService(WalletServiceABC):
    def __init__(self, uow: UnitOfWorkABC):
        self._uow = uow

    async def make_wallet_preffered(
        self, *, wallet_id: UUID, account_id: UUID, preferred: bool
    ) -> Wallet:
        async with self._uow:
            wallet = await self._uow.wallet_repository.get(entity_id=wallet_id)
            if not wallet or wallet.account_id != account_id:
                raise WalletNotFoundException()
            wallet.preffered = preferred
            await self._uow.commit()
        return wallet
