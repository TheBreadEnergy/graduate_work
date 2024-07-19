from abc import ABC, abstractmethod
from uuid import UUID

from src.exceptions.wallet import WalletNotFoundException
from src.models.domain.wallet import Wallet
from src.repositories.wallet import WalletRepositoryABC


class WalletQueryServiceABC(ABC):
    @abstractmethod
    async def get_wallet(self, *, account_id: UUID) -> Wallet:
        ...


class WalletQueryService(WalletQueryServiceABC):
    def __init__(self, wallet_repository: WalletRepositoryABC):
        self._repo = wallet_repository

    async def get_wallet(self, *, account_id: UUID) -> Wallet:
        wallet = await self._repo.get_for_user(account_id=account_id)
        if not wallet:
            raise WalletNotFoundException()
        return wallet
