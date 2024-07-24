import json
from abc import ABC, abstractmethod

from aiokafka import AIOKafkaProducer
from fastapi.encoders import jsonable_encoder
from src.core.settings import settings
from src.models.events.payment import (
    PaymentCancelledEvent,
    PaymentCreatedEvent,
    PaymentEventABC,
    PaymentSuccessEvent,
)
from src.models.events.refund import (
    RefundCancelledEvent,
    RefundCreatedEvent,
    RefundEventABC,
    RefundSuccessEvent,
)


class EventHandlerABC(ABC):
    @abstractmethod
    async def handle_payment_event(self, event: PaymentEventABC):
        ...

    @abstractmethod
    async def handle_refund_event(self, event: RefundEventABC):
        ...


class KafkaEventHandler(EventHandlerABC):
    def __init__(self, kafka_producer: AIOKafkaProducer):
        self._producer = kafka_producer

    async def handle_payment_event(self, event: PaymentEventABC):
        topic = self._get_topic_for_payment(event)
        await self._producer.send(
            topic=topic,
            value=json.dumps(jsonable_encoder(event)).encode(),
            key=str(event.payment_id).encode(),
        )

    async def handle_refund_event(self, event: RefundEventABC):
        topic = self._get_topic_for_refund(event)
        await self._producer.send(
            topic=topic,
            value=json.dumps(jsonable_encoder(event)).encode(),
            key=str(event.refund_id).encode(),
        )

    def _get_topic_for_payment(self, event: PaymentEventABC) -> str:
        match event:
            case PaymentCreatedEvent():
                return settings.payment_created_topic
            case PaymentCancelledEvent():
                return settings.payment_cancelled_topic
            case PaymentSuccessEvent():
                return settings.payment_success_topic
            case _:
                raise NotImplementedError("Неподдерживаемый тип событий")

    def _get_topic_for_refund(self, event: RefundEventABC):
        match event:
            case RefundCreatedEvent():
                return settings.refund_created_topic
            case RefundCancelledEvent():
                return settings.refund_cancelled_topic
            case RefundSuccessEvent():
                return settings.refund_success_topic
            case _:
                raise NotImplementedError("Неподдерживаемый тип событий")
