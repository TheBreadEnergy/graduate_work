from abc import ABC, abstractmethod
from uuid import UUID

from src.core.settings import settings
from src.enums.payment import PaymentStatus
from src.exceptions.external import ExternalIpNotTrustedException
from src.models.events.payment import PaymentCancelledEvent, PaymentSuccessEvent
from src.models.events.refund import RefundSuccessEvent
from src.schemas.v1.billing.events import EventSchema
from src.services.event_handler import EventHandlerABC
from src.services.uow import UnitOfWorkABC
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
    def __init__(self, event_handler: EventHandlerABC, uow: UnitOfWorkABC):
        self._handler = event_handler
        self._uow = uow

    async def process_event(self, event: EventSchema, ip_address: str | None = None):
        if not SecurityHelper().is_ip_trusted(ip_address) and not settings.dev:
            raise ExternalIpNotTrustedException(ip_address)
        notification = WebhookNotificationFactory().create(event.model_dump())
        event = notification.object
        match notification.event:
            case WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                payment_event = PaymentSuccessEvent(payment_id=event.id)
                await self._handler.handle_payment_event(payment_event)
                await self._handle_payment_status(event.id, PaymentStatus.succeeded)
            case WebhookNotificationEventType.PAYMENT_CANCELED:
                payment_event = PaymentCancelledEvent(
                    payment_id=event.id,
                    reason=event.cancellation_details.reason,
                )
                await self._handle_payment_status(event.id, PaymentStatus.cancelled)
                await self._handler.handle_payment_event(payment_event)
            case WebhookNotificationEventType.REFUND_SUCCEEDED:
                refund_event = RefundSuccessEvent(refund_id=event.id)
                await self._handle_refund_status(
                    refund_id=event.id, status=PaymentStatus.succeeded
                )
                await self._handler.handle_refund_event(refund_event)
            case _:
                raise NotImplementedError("Неподдерживаемое событие")

    async def _handle_payment_status(self, payment_id: str, status: PaymentStatus):
        async with self._uow:
            payment = await self._uow.payment_repository.payment_by_external_id(
                payment_id=UUID(payment_id)
            )
            if payment:
                payment.status = status
            await self._uow.commit()

    async def _handle_refund_status(self, refund_id: str, status: PaymentStatus):
        async with self._uow:
            refund = await self._uow.refund_repository.get_by_external(
                refund_id=UUID(refund_id)
            )
            if refund:
                refund.status = status
            await self._uow.commit()
