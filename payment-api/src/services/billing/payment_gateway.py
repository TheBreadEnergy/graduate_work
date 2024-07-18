import uuid
from abc import ABC, abstractmethod
from uuid import UUID

import yookassa
from src.core.settings import settings
from src.models.domain.payment import Payment
from src.schemas.v1.billing.payments import PayMethod, PaySchema, PayStatusSchema
from src.schemas.v1.billing.refunds import RefundStatusSchema
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
