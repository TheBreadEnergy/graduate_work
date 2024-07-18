import decimal
from uuid import UUID

import grpc.aio
from src.core.grpc.models.payment_pb2 import (
    BatchSubscriptionPaymentRequest,
    BatchSubscriptionPaymentResponse,
    SubscriptionPaymentRequest,
    SubscriptionPaymentResponse,
)
from src.core.grpc.services.payment_pb2_grpc import PaymentManagerServicer
from src.exceptions.external import ExternalPaymentUnavailableException
from src.repositories.payment import PaymentRepositoryABC
from src.schemas.v1.billing.payments import PayStatusSchema
from src.schemas.v1.billing.subscription import (
    BatchSubscriptions,
    SubscriptionPaymentData,
)
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.services.billing.payment_gateway import PaymentGatewayABC, process_payment
from src.services.uow import UnitOfWorkABC


async def make_batch_payment(
    self, subscription_lists: BatchSubscriptions
) -> list[PayStatusSchema]:
    answers = []
    async with self._uow:
        for subscription_data in subscription_lists.subscriptions:
            status = process_payment(self._gateway, subscription_data)
            payment = PaymentCreateSchema(
                account_id=subscription_data.account_id,
                description=subscription_data.subscription_name,
                subscription_id=subscription_data.subscription_id,
                price=subscription_data.price,
                status=status.status,
                reason=status.reason,
            )
            self._payment_repo.insert(data=payment)
            answers.append(status)
        await self._uow.commit()
    return answers


class GrpcPaymentService(PaymentManagerServicer):
    def __init__(
        self,
        payment_gateway: PaymentGatewayABC,
        payment_repo: PaymentRepositoryABC,
        uow: UnitOfWorkABC,
    ):
        self._gateway = payment_gateway
        self._payment_repo = payment_repo
        self._uow = uow

    def _make_payment(self, request: SubscriptionPaymentRequest) -> PayStatusSchema:
        subscription_payment = SubscriptionPaymentData(
            subscription_id=UUID(request.subscription_id),
            account_id=UUID(request.account_id),
            subscription_name=request.subscription_name,
            price=decimal.Decimal(request.price),
            currency=request.currency,
            wallet_id=UUID(request.wallet_id),
        )
        response = process_payment(
            self._gateway,
            subscription_data=subscription_payment,
        )
        return response

    async def Pay(
        self, request: SubscriptionPaymentRequest, context: grpc.aio.ServicerContext
    ):

        try:
            response = self._make_payment(request)
            async with self._uow:
                payment_data = PaymentCreateSchema(
                    account_id=UUID(request.account_id),
                    description=request.subscription_name,
                    subscription_id=UUID(request.subscription_id),
                    price=decimal.Decimal(request.price),
                    status=response.status,
                    reason=response.reason,
                )
                self._payment_repo.insert(data=payment_data)
                await self._uow.commit()
            return SubscriptionPaymentResponse(
                status=str(response.status), reason=response.reason
            )
        except ExternalPaymentUnavailableException as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(e.message)
            raise e

    async def PayBatch(
        self,
        request: BatchSubscriptionPaymentRequest,
        context: grpc.aio.ServicerContext,
    ):
        results = []
        async with self._uow:
            try:
                for subscription in request.requests:
                    response = self._make_payment(subscription)
                    payment_data = PaymentCreateSchema(
                        account_id=UUID(subscription.account_id),
                        description=subscription.subscription_name,
                        subscription_id=UUID(subscription.subscription_id),
                        price=decimal.Decimal(subscription.price),
                        status=response.status,
                        reason=response.reason,
                    )
                    self._payment_repo.insert(data=payment_data)
                    results.append(
                        SubscriptionPaymentResponse(
                            status=str(response.status), reason=response.reason
                        )
                    )
                await self._uow.commit()
                return BatchSubscriptionPaymentResponse(responses=results)
            except ExternalPaymentUnavailableException as e:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details(e.message)
                raise e
