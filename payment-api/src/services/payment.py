from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.models.domain.payment import Payment
from src.repositories.payment import PaymentRepositoryABC
from src.repositories.wallet import WalletRepositoryABC
from src.schemas.v1.billing.payments import PayStatusSchema
from src.schemas.v1.billing.subscription import SubscriptionPaymentData
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.schemas.v1.crud.wallets import WalletCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC, process_payment
from src.services.subscription import SubscriptionManagerABC
from src.services.uow import UnitOfWorkABC


class PaymentQueryServiceABC(ABC):
    @abstractmethod
    async def get_payments(
        self, account_id: UUID | None = None
    ) -> PaginatedPage[Payment]:
        ...

    @abstractmethod
    async def get_payment(self, payment_id: UUID) -> Payment:
        ...


class PaymentQueryService(PaymentQueryServiceABC):
    def __init__(self, payment_repository: PaymentRepositoryABC):
        self._repo = payment_repository

    async def get_payments(
        self, account_id: UUID | None = None
    ) -> PaginatedPage[Payment]:
        return await self._repo.gets(account_id=account_id)

    async def get_payment(self, payment_id: UUID) -> Payment:
        return await self._repo.get(entity_id=payment_id)


class PaymentServiceABC(ABC):
    @abstractmethod
    def make_payment(
        self,
        subscription_id: UUID,
        account_id,
        save_payment_method: bool,
    ) -> PayStatusSchema:
        ...


# TODO: Refractor payment_service
class PaymentService(PaymentServiceABC):
    def __init__(
        self,
        payment_gateway: PaymentGatewayABC,
        payment_repo: PaymentRepositoryABC,
        wallet_repository: WalletRepositoryABC,
        subscription_manager: SubscriptionManagerABC,
        uow: UnitOfWorkABC,
    ):
        self._gateway = payment_gateway
        self._payment_repo = payment_repo
        self._wallet_repo = wallet_repository
        self._subscription_service = subscription_manager
        self._uow = uow

    async def make_payment(
        self,
        subscription_id: UUID,
        account_id: UUID,
        save_payment_method: bool,
    ) -> PayStatusSchema:
        subscription = await self._subscription_service.get_subscription(
            subscription_id=subscription_id
        )

        subscription_payment_data = SubscriptionPaymentData(
            subscription_id=subscription.subscription_id,
            account_id=account_id,
            subscription_name=subscription.name,
            price=subscription.price,
            currency=subscription.currency,
        )
        status = process_payment(
            self._gateway,
            subscription_payment_data,
            save_payment_method=save_payment_method,
        )
        async with self._uow:
            payment = PaymentCreateSchema(
                account_id=account_id,
                description=subscription.subscription_name,
                subscription_id=subscription.subscription_id,
                price=subscription.price,
                status=status.status,
                reason=status.reason,
            )
            self._payment_repo.insert(payment)
            if save_payment_method:
                wallet = WalletCreateSchema(
                    account_id=account_id,
                    payment_method_id=status.payment_information.payment_id,
                    title=status.payment_information.title,
                    reccurent=save_payment_method,
                )
                self._wallet_repo.insert(data=wallet)
            await self._uow.commit()
        return status
