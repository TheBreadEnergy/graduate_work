import decimal
from abc import ABC, abstractmethod
from uuid import UUID

from src.core.pagination import PaginatedPage
from src.enums.payment import PaymentStatus
from src.exceptions.payment import PaymentNotFoundException
from src.models.domain.payment import Payment
from src.models.events.payment import PaymentCreatedEvent
from src.repositories.payment import PaymentRepositoryABC
from src.schemas.v1.billing.payments import PayStatusSchema
from src.schemas.v1.billing.subscription import SubscriptionPaymentData
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.schemas.v1.crud.wallets import WalletCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC, process_payment
from src.services.event_handler import EventHandlerABC
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

    @abstractmethod
    async def filter_payments_by_status(
        self, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        ...


class PaymentQueryService(PaymentQueryServiceABC):
    def __init__(self, payment_repository: PaymentRepositoryABC):
        self._repo = payment_repository

    async def get_payments(
        self, account_id: UUID | None = None
    ) -> PaginatedPage[Payment]:
        return await self._repo.gets(account_id=account_id)

    async def get_payment(self, payment_id: UUID) -> Payment:
        payment = await self._repo.get(entity_id=payment_id)
        if not payment:
            raise PaymentNotFoundException()
        return payment

    async def filter_payments_by_status(
        self, status: PaymentStatus
    ) -> PaginatedPage[Payment]:
        return await self._repo.filter_by_status(status=status)


class PaymentServiceABC(ABC):
    @abstractmethod
    def make_payment(
        self,
        subscription_id: UUID,
        subscription_name: str,
        price: decimal.Decimal,
        currency: str,
        account_id: UUID,
        save_payment_method: bool,
        payment_method: str | None = None,
    ) -> PayStatusSchema:
        ...


class PaymentService(PaymentServiceABC):
    def __init__(
        self,
        payment_gateway: PaymentGatewayABC,
        event_hander: EventHandlerABC,
        uow: UnitOfWorkABC,
    ):
        self._uow = uow
        self._gateway = payment_gateway
        self._handler = event_hander

    async def make_payment(
        self,
        subscription_id: UUID,
        subscription_name: str,
        price: decimal.Decimal,
        currency: str,
        account_id: UUID,
        save_payment_method: bool,
        payment_method: str | None = None,
    ) -> PayStatusSchema:
        subscription_payment_data = SubscriptionPaymentData(
            subscription_id=subscription_id,
            account_id=account_id,
            subscription_name=subscription_name,
            price=price,
            currency=currency,
            payment_method=payment_method,
        )
        status = process_payment(
            self._gateway,
            subscription_payment_data,
            save_payment_method=save_payment_method,
        )
        async with self._uow:
            payment = PaymentCreateSchema(
                account_id=account_id,
                description=subscription_name,
                payment_id=status.payment_id,
                subscription_id=subscription_id,
                price=price,
                currency=currency,
                status=status.status,
                reason=status.reason,
            )
            payment_database: Payment = self._uow.payment_repository.insert(
                data=payment
            )
            if save_payment_method and status.payment_information:
                wallet = WalletCreateSchema(
                    account_id=account_id,
                    payment_method_id=status.payment_information.payment_id,
                    title=status.payment_information.title,
                    reccurent_payment=save_payment_method,
                )
                await self._uow.wallet_repository.insert(data=wallet)
            await self._uow.commit()
        payment_event = PaymentCreatedEvent(
            user_id=account_id,
            license_id=payment.subscription_id,
            payment_id=payment_database.id,
        )
        await self._handler.handle_payment_event(payment_event)
        return status
