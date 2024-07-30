import logging
from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.broker.rabbit import RabbitMessageBroker
from src.core.config import settings
from src.database.postgres import async_session_subscriptions, get_session
from src.enums.payment import PaymentStatus
from src.models.payment import Payment
from src.models.refund import Refund
from src.models.user_subscription import UserSubscription
from src.schemas.events.payment import (
    PaymentCancelledEvent,
    PaymentEventABC,
    PaymentSuccessEvent,
)
from src.schemas.events.refund import (
    RefundCancelledEvent,
    RefundEventABC,
    RefundSuccessEvent,
)
from src.schemas.notify import NotifyMessage

logger = logging.getLogger(__name__)


class EventHandlerABC(ABC):
    @abstractmethod
    async def handle_payment_event(self, db: AsyncSession, event: PaymentEventABC):
        ...

    @abstractmethod
    async def handle_refund_event(self, db: AsyncSession, event: RefundEventABC):
        ...


class KafkaEventHandler(EventHandlerABC):
    def __init__(self):
        self.rabbitmq_client = RabbitMessageBroker(
            host=settings.rabbit_host,
            port=settings.rabbit_port,
            username=settings.rabbit_login,
            password=settings.rabbit_password,
        )

    async def handle_payment_event(self, db: AsyncSession, event: PaymentEventABC):

        payment = (
            (
                await db.execute(
                    select(Payment).where(Payment.payment_id == event.payment_id)
                )
            )
            .scalars()
            .one_or_none()
        )
        if payment:
            await self.check_status_and_notify(payment, event)

    async def handle_refund_event(self, db: AsyncSession, event: RefundEventABC):
        refund = (
            (
                await db.execute(
                    select(Refund).where(Refund.refund_id == event.refund_id)
                )
            )
            .scalars()
            .one_or_none()
        )
        if refund:
            await self.check_status_and_notify(refund, event)

    async def check_status_and_notify(self, obj, event):
        if isinstance(event, (PaymentCancelledEvent, RefundCancelledEvent)):
            if obj.status != PaymentStatus.cancelled:
                logger.error(
                    f"{obj.__class__.__name__} {obj.id} does not have status {PaymentStatus.cancelled}"
                )
                return
            await self.send_notification(self.get_routing_key(event), obj)
        elif isinstance(event, (PaymentSuccessEvent, RefundSuccessEvent)):
            # if obj.status != PaymentStatus.succeeded:
            #     logger.error(
            #         f"{obj.__class__.__name__} {obj.id} does not have status {PaymentStatus.succeeded}"
            #     )
            #     return

            async for db_subscriptions in get_session(async_session_subscriptions):
                user_subscription = (
                    (
                        await db_subscriptions.execute(
                            select(UserSubscription).where(
                                UserSubscription.user_id == obj.account_id
                            )
                        )
                    )
                    .scalars()
                    .one_or_none()
                )
                if user_subscription:
                    if isinstance(event, PaymentSuccessEvent):
                        user_subscription.last_payed = datetime.now()
                        user_subscription.active = True
                    elif isinstance(event, RefundSuccessEvent):
                        user_subscription.active = False
                else:
                    if isinstance(event, PaymentSuccessEvent):
                        user_subscription = UserSubscription(
                            user_id=obj.account_id,
                            subscription_id=obj.subscription_id,
                            price=obj.price,
                            currency=obj.currency,
                            promo_id=None,
                            active=True,
                            last_payed=datetime.now(),
                        )
                        db_subscriptions.add(user_subscription)
                await db_subscriptions.commit()

            await self.send_notification(self.get_routing_key(event), obj)

    async def send_notification(self, routing_key: str, obj):
        await self.rabbitmq_client.startup()
        routing_key = f"{settings.routing_prefix}.{settings.supported_message_versions[0]}.{routing_key}"
        message = NotifyMessage(
            id=obj.id, payment_id=obj.payment_id, account_id=obj.account_id
        ).json()
        await self.rabbitmq_client.publish(message.encode("utf-8"), routing_key)
        await self.rabbitmq_client.shutdown()

    def get_routing_key(self, event):
        if isinstance(event, PaymentCancelledEvent):
            return settings.payment_cancelled_key
        elif isinstance(event, PaymentSuccessEvent):
            return settings.payment_success_key
        elif isinstance(event, RefundCancelledEvent):
            return settings.refund_cancelled_key
        elif isinstance(event, RefundSuccessEvent):
            return settings.refund_success_key
        return ""
