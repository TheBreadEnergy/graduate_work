from abc import ABC, abstractmethod
from uuid import UUID

from requests import RequestException
from src.core.pagination import PaginatedPage
from src.exceptions.external import ExternalPaymentUnavailableException
from src.models.domain.payment import Payment
from src.repositories.payment import PaymentRepositoryABC
from src.schemas.v1.billing.payments import (
    PaySchema,
    PayStatusSchema,
    ProductInformation,
)
from src.schemas.v1.billing.subscription import (
    BatchSubscriptions,
    SubscriptionPaymentData,
)
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC
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
        subscription_manager: SubscriptionManagerABC,
    ) -> PayStatusSchema:
        ...

    @abstractmethod
    def make_batch_payment(
        self, subscription_lists: BatchSubscriptions
    ) -> list[PayStatusSchema]:
        ...


class PaymentService(PaymentServiceABC):
    def __init__(
        self,
        payment_gateway: PaymentGatewayABC,
        payment_repo: PaymentRepositoryABC,
        uow: UnitOfWorkABC,
    ):
        self._gateway = payment_gateway
        self._repo = payment_repo
        self._uow = uow

    async def make_payment(
        self,
        subscription_id: UUID,
        account_id: UUID,
        subscription_manager: SubscriptionManagerABC,
    ) -> PayStatusSchema:
        subscription = await subscription_manager.get_subscription(
            subscription_id=subscription_id
        )

        subscription_payment_data = SubscriptionPaymentData(
            subscription_id=subscription.subscription_id,
            account_id=account_id,
            subscription_name=subscription.name,
            price=subscription.price,
            currency=subscription.currency,
        )
        status = self._process_payment(subscription_payment_data)
        async with self._uow:
            payment = PaymentCreateSchema(
                account_id=account_id,
                description=subscription.subscription_name,
                subscription_id=subscription.subscription_id,
                price=subscription.price,
                status=status.status,
                reason=status.reason,
            )
            self._repo.insert(payment)
            await self._uow.commit()
        return status

    async def make_batch_payment(
        self, subscription_lists: BatchSubscriptions
    ) -> list[PayStatusSchema]:
        answers = []
        async with self._uow:
            for subscription_data in subscription_lists.subscriptions:
                status = self._process_payment(subscription_data)
                payment = PaymentCreateSchema(
                    account_id=subscription_data.account_id,
                    description=subscription_data.subscription_name,
                    subscription_id=subscription_data.subscription_id,
                    price=subscription_data.price,
                    status=status.status,
                    reason=status.reason,
                )
                self._repo.insert(data=payment)
                answers.append(status)
            await self._uow.commit()
        return answers

    def _process_payment(
        self, subscription_data: SubscriptionPaymentData
    ) -> PayStatusSchema:
        idempotency_key = (
            f"{subscription_data.account_id}_{subscription_data.subscription_id}"
        )
        request = PaySchema(
            description=subscription_data.subscription_name,
            product_information=ProductInformation(
                product_id=subscription_data.subscription_id,
                product_name=subscription_data.subscription_name,
                price=subscription_data.price,
                currency=subscription_data.currency,
            ),
            save_payment_method=False,
        )
        try:
            status = self._gateway.create_payment(
                payment_data=request,
                wallet_id=subscription_data.wallet_id,
                idempotency_key=idempotency_key,
            )
        except RequestException as e:
            raise ExternalPaymentUnavailableException(message=e.response.reason) from e
        return status
