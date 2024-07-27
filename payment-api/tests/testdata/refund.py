import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from src.enums.payment import PaymentStatus
from src.models.domain.payment import Payment
from src.models.domain.refund import Refund
from src.models.events.refund import RefundCreatedEvent
from src.schemas.v1.billing.refunds import RefundStatusSchema
from src.schemas.v1.crud.refunds import RefundCreateSchema
from tests.testdata.payment import generate_test_payment


class RefundTestData(BaseModel):
    refund_status: RefundStatusSchema
    refund: Refund
    payment: Payment
    refund_create_schema: RefundCreateSchema
    refund_event: RefundCreatedEvent

    model_config = ConfigDict(arbitrary_types_allowed=True)


def generate_test_refund(mock_id: uuid.UUID | None = None):
    if not mock_id:
        mock_id = uuid.uuid4()
    return Refund(
        account_id=mock_id,
        payment_id=mock_id,
        money=Decimal(800),
        status=PaymentStatus.success,
        reason=None,
        id=mock_id,
    )


def generate_test_refund_service_data() -> RefundTestData:
    mock_id = uuid.uuid4()
    refund_status = RefundStatusSchema(
        status=PaymentStatus.success, payment_id=mock_id, reason=None
    )
    refund = generate_test_refund(mock_id)
    payment = generate_test_payment(mock_id)
    refund_create_schema = RefundCreateSchema(
        account_id=mock_id,
        payment_id=mock_id,
        description="",
        money=Decimal(800),
        status=PaymentStatus.success,
        reason=None,
    )

    refund_event = RefundCreatedEvent(
        refund_id=mock_id,
        user_id=mock_id,
        license_id=mock_id,
    )
    return RefundTestData(
        refund_status=refund_status,
        refund=refund,
        payment=payment,
        refund_create_schema=refund_create_schema,
        refund_event=refund_event,
    )


REFUND = generate_test_refund()

REFUND_DATASET = [generate_test_refund_service_data()]
