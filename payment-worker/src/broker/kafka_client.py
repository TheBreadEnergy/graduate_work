import json
from typing import List

import backoff
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError, KafkaTimeoutError, NoBrokersAvailable

from src.broker.base import AbstractKafkaClient
from src.core.config import settings
from src.database.postgres import async_session_payments, get_session
from src.handlers.event_handler import KafkaEventHandler
from src.schemas.events.payment import PaymentCancelledEvent, PaymentSuccessEvent
from src.schemas.events.refund import RefundSuccessEvent


class KafkaClient(AbstractKafkaClient):
    def __init__(
        self,
        bootstrap_servers,
        client_id,
        topic_names: List[str],
        group_id="payment-group",
    ):
        super().__init__()
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.topic_names = topic_names
        self.group_id = group_id

    @backoff.on_exception(
        backoff.expo, (KafkaError, KafkaTimeoutError, NoBrokersAvailable), max_tries=5
    )
    async def consume_messages(self):
        consumer = AIOKafkaConsumer(
            *self.topic_names,
            bootstrap_servers=self.bootstrap_servers,
            client_id=self.client_id,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
        )

        await consumer.start()
        try:
            async for msg in consumer:
                if msg.value is not None:
                    self.logger.info(f"Received message: {msg.value}")
                    await self.process_message(msg)
                else:
                    self.logger.warning("Received message with None value")
        except KafkaError as e:
            self.logger.error(f"Error while consuming messages: {e}")
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error while consuming messages: {e}")
        finally:
            await consumer.stop()

    async def process_message(self, msg):
        event_data = msg.value
        async for db in get_session(async_session_payments):
            handler = KafkaEventHandler()
            if msg.topic == settings.payment_success_topic:
                event = PaymentSuccessEvent(**event_data)
                await handler.handle_payment_event(db, event)
            elif msg.topic == settings.payment_cancelled_topic:
                event = PaymentCancelledEvent(**event_data)
                await handler.handle_payment_event(db, event)
            elif msg.topic == settings.refund_success_topic:
                event = RefundSuccessEvent(**event_data)
                await handler.handle_refund_event(db, event)
