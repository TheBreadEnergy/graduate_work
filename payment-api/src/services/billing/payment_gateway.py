import uuid
from abc import ABC, abstractmethod
from uuid import UUID

import yookassa
from requests import RequestException
from src.core.settings import settings
from src.enums.payment import PaymentStatus
from src.exceptions.external import ExternalPaymentUnavailableException
from src.models.domain.payment import Payment
from src.schemas.v1.billing.payments import (
    PayMethod,
    PaySchema,
    PayStatusSchema,
    ProductInformation,
)
from src.schemas.v1.billing.refunds import RefundStatusSchema
from src.schemas.v1.billing.subscription import SubscriptionPaymentData
from yookassa import Refund
from yookassa.domain.common import ConfirmationType
from yookassa.domain.models.payment_data.payment_data import ResponsePaymentData
from yookassa.domain.request import PaymentRequestBuilder


class PaymentGatewayABC(ABC):
    @abstractmethod
    def create_payment(
        self,
        payment_data: PaySchema,
        wallet_id: UUID | None = None,
        idempotency_key: str | None = None,
    ) -> PayStatusSchema:
        ...

    @abstractmethod
    def create_refund(self, payment: Payment, description: str | None = None):
        ...

    @abstractmethod
    def cancel_payment(
        self, payment_id: UUID, idempotency_key: UUID | None = None
    ) -> PayStatusSchema:
        ...


class YooKassaPaymentGateway(PaymentGatewayABC):
    def create_payment(
        self,
        payment_data: PaySchema,
        wallet_id: UUID | None = None,
        idempotency_key: str | None = None,
    ) -> PayStatusSchema:
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        builder = PaymentRequestBuilder()
        (
            builder.set_amount(
                {
                    "value": payment_data.product_information.price,
                    "currency": payment_data.product_information.currency,
                }
            )
            .set_capture(settings.capture)
            .set_description(payment_data.description)
            .set_metadata(
                {"subscription_id": str(payment_data.product_information.product_id)}
            )
        )
        if wallet_id:
            builder.set_payment_method_id(str(wallet_id))
        if not wallet_id and payment_data.save_payment_method:
            builder.set_save_payment_method(True)
        builder.set_confirmation(
            {"type": ConfirmationType.REDIRECT, "return_url": settings.redirect_url}
        )
        request = builder.build()
        result = yookassa.Payment.create(request, idempotency_key=str(idempotency_key))
        payment_payload: ResponsePaymentData = result.payment_method
        return PayStatusSchema(
            status=result.status,
            confirmation_url=(
                result.confirmation.confirmation_url if not wallet_id else None
            ),
            reason=(
                result.cancellation_details.reason
                if result.cancellation_details.reason
                else None
            ),
            payment_method=(
                PayMethod(title=payment_payload.title, payment_id=payment_payload.id)
                if payment_data.save_payment_method or result.payment_method
                else None
            ),
        )

    def cancel_payment(
        self, payment_id: UUID, idempontancy_key: str | None = None
    ) -> PayStatusSchema:
        if not idempontancy_key:
            idempontancy_key = str(uuid.uuid4())
        result = yookassa.Payment.cancel(
            payment_id=payment_id, idempotency_key=idempontancy_key
        )
        return PayStatusSchema(
            status=result.status,
            confirmation_url=result.confirmation.confirmation_url,
            reason=(
                result.cancellation_details.reason
                if result.cancellation_details
                else None
            ),
        )

    async def create_refund(self, payment: Payment, description: str | None = None):
        result = Refund.create(
            {
                "amount": {"value": payment.price, "currency": payment.currency},
                "payment_id": str(payment.id),
                "description": payment.description if payment.description else "",
            },
        )
        return RefundStatusSchema(
            status=result.status,
            payment_id=payment.id,
            reason=(
                result.cancellation_details.reason
                if result.cancellation_details
                else None
            ),
        )


class MockPaymentGateway(PaymentGatewayABC):
    def create_payment(
        self,
        payment_data: PaySchema,
        wallet_id: UUID | None = None,
        idempotency_key: str | None = None,
    ) -> PayStatusSchema:
        return PayStatusSchema(
            status=PaymentStatus.success,
            confirmation_url=None,
            reason=None,
            payment_method=(
                PayMethod(title="Mock payment", payment_id=uuid.uuid4())
                if payment_data.save_payment_method
                else None
            ),
        )

    def create_refund(self, payment: Payment, description: str | None = None):
        return RefundStatusSchema(
            status=PaymentStatus.success, payment_id=payment.id, reason=None
        )

    def cancel_payment(
        self, payment_id: UUID, idempotency_key: UUID | None = None
    ) -> PayStatusSchema:
        return PayStatusSchema(
            status=PaymentStatus.cancelled,
            confirmation_url=None,
            reason=None,
            payment_method=None,
        )


def process_payment(
    gateway: PaymentGatewayABC,
    subscription_data: SubscriptionPaymentData,
    save_payment_method: bool = False,
):
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
        save_payment_method=save_payment_method,
    )
    try:
        status = gateway.create_payment(
            payment_data=request,
            wallet_id=subscription_data.wallet_id,
            idempotency_key=idempotency_key,
        )
        return status
    except RequestException as e:
        raise ExternalPaymentUnavailableException(message=e.response.reason) from e
