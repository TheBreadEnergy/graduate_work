import uuid

from src.core.settings import settings
from src.models.events.payment import (
    PaymentCancelledEvent,
    PaymentCreatedEvent,
    PaymentSuccessEvent,
)
from src.models.events.refund import (
    RefundCancelledEvent,
    RefundCreatedEvent,
    RefundSuccessEvent,
)


def generate_payment_events():
    mock_id = uuid.uuid4()
    return [
        (
            PaymentCreatedEvent(
                payment_id=mock_id, user_id=mock_id, license_id=mock_id
            ),
            settings.payment_created_topic,
        ),
        (PaymentSuccessEvent(payment_id=mock_id), settings.payment_success_topic),
        (
            PaymentCancelledEvent(payment_id=mock_id, reason=""),
            settings.payment_cancelled_topic,
        ),
    ]


def generate_refund_events():
    mock_id = uuid.uuid4()
    return [
        (
            RefundCreatedEvent(refund_id=mock_id, user_id=mock_id),
            settings.refund_created_topic,
        ),
        (RefundSuccessEvent(refund_id=mock_id), settings.refund_success_topic),
        (
            RefundCancelledEvent(refund_id=mock_id, reason=""),
            settings.refund_cancelled_topic,
        ),
    ]


PAYMENT_EVENTS = generate_payment_events()
REFUND_EVENTS = generate_refund_events()
