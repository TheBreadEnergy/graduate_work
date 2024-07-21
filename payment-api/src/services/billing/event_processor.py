from abc import ABC, abstractmethod

from src.core.settings import settings
from src.exceptions.external import ExternalIpNotTrustedException
from src.models.events.payment import PaymentCancelledEvent, PaymentSuccessEvent
from src.models.events.refund import RefundSuccessEvent
from src.schemas.v1.billing.events import EventSchema
from src.services.event_handler import EventHandlerABC
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)


class BillingEventProcessorABC(ABC):
    @abstractmethod
    async def process_event(self, event: EventSchema, ip_address: str | None = None):
        ...


class YookassaBillingEventProcessor(BillingEventProcessorABC):
    def __init__(self, event_handler: EventHandlerABC):
        self._handler = event_handler

    async def process_event(self, event: EventSchema, ip_address: str | None = None):
        if not SecurityHelper().is_ip_trusted(ip_address) or not settings.debug:
            raise ExternalIpNotTrustedException(ip_address)
        notification = WebhookNotificationFactory().create(event.model_dump())
        event = notification.object
        match notification.event:
            case WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                payment_event = PaymentSuccessEvent(payment_id=event.id)
                await self._handler.handle_payment_event(payment_event)
            case WebhookNotificationEventType.PAYMENT_CANCELED:
                payment_event = PaymentCancelledEvent(
                    payment_id=event.id,
                    reason=event.cancellation_details.reason,
                )
                await self._handler.handle_payment_event(payment_event)
            case WebhookNotificationEventType.REFUND_SUCCEEDED:
                refund_event = RefundSuccessEvent(refund_id=event.id)
                await self._handler.handle_refund_event(refund_event)
            case _:
                raise NotImplementedError("Неподдерживаемое событие")
