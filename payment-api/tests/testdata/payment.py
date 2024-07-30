import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from src.enums.payment import PaymentStatus
from src.models.domain.payment import Payment
from src.models.events.payment import PaymentCreatedEvent
from src.schemas.v1.billing.payments import (
    PayMethod,
    PaySchema,
    PayStatusSchema,
    ProductInformation,
)
from src.schemas.v1.crud.payments import PaymentCreateSchema
from src.schemas.v1.crud.wallets import WalletCreateSchema


class PaymentTestData(BaseModel):
    payment: Payment
    pay_status: PayStatusSchema
    pay_schema: PaySchema
    payment_create_schema: PaymentCreateSchema
    wallet: WalletCreateSchema | None
    payment_event: PaymentCreatedEvent

    model_config = ConfigDict(arbitrary_types_allowed=True)


def generate_test_payment(payment_id: uuid.UUID | None = None):
    if not payment_id:
        payment_id = uuid.uuid4()
    return Payment(
        id=payment_id,
        account_id=payment_id,
        payment_id=payment_id,
        subscription_id=payment_id,
        price=Decimal(800),
        currency="RUB",
        status=PaymentStatus.succeeded,
        idempotency_key=str(payment_id),
        description="",
        reason=None,
        created=datetime.datetime.now(datetime.timezone.utc),
    )


def generate_test_pay_status(mock_id: uuid.UUID, with_payment_info: bool = True):
    return PayStatusSchema(
        payment_id=mock_id,
        status=PaymentStatus.succeeded,
        redirection_url="",
        reason=None,
        payment_information=(
            PayMethod(title="Mock payment", payment_id=mock_id)
            if with_payment_info
            else None
        ),
    )


def generate_payment_test_data(save_method: bool):
    mock_id = uuid.uuid4()
    payment: Payment = generate_test_payment(mock_id)
    pay_status: PayStatusSchema = generate_test_pay_status(
        mock_id, with_payment_info=save_method
    )

    pay_schema = PaySchema(
        description=str(mock_id),
        product_information=ProductInformation(
            product_id=payment.subscription_id,
            product_name=str(payment.subscription_id),
            price=payment.price,
            currency=payment.currency,
        ),
        payment_method="bank_card",
        save_payment_method=save_method,
    )

    payment_create_schema = PaymentCreateSchema(
        account_id=mock_id,
        description=str(mock_id),
        payment_id=str(mock_id),
        subscription_id=mock_id,
        price=payment.price,
        currency=payment.currency,
        status=PaymentStatus.succeeded,
        reason=None,
    )
    wallet: WalletCreateSchema | None = None
    if save_method:
        wallet = WalletCreateSchema(
            account_id=mock_id,
            payment_method_id=mock_id,
            title="Mock payment",
            reccurent_payment=True,
        )
    payment_event = PaymentCreatedEvent(
        user_id=mock_id,
        license_id=payment.subscription_id,
        payment_id=mock_id,
    )
    return PaymentTestData(
        payment=payment,
        payment_create_schema=payment_create_schema,
        pay_schema=pay_schema,
        wallet=wallet,
        payment_event=payment_event,
        pay_status=pay_status,
    )


PAYMENT = generate_test_payment()
DATASET_WITH_SAVE_METHOD = [generate_payment_test_data(save_method=True)]
DATASET_WITHOUT_SAVE_METHOD = [generate_payment_test_data(save_method=False)]
