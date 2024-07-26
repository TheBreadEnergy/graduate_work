import json
import logging
from datetime import datetime

import aio_pika
import backoff
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractRobustConnection,
    ExchangeType,
)

from src.broker.base import MessageBrokerABC
from src.core.config import ROUTING_KEYS, settings

logger = logging.getLogger(__name__)


class RabbitMessageBroker(MessageBrokerABC):
    def __init__(self, host: str, port: int, username: str, password: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self.exchange: AbstractExchange | None = None

    @backoff.on_exception(wait_gen=backoff.expo, max_tries=3, exception=Exception)
    async def startup(self) -> None:
        self._connection = await aio_pika.connect_robust(
            host=self._host,
            port=self._port,
            login=self._username,
            password=self._password,
        )

        self._channel = await self._connection.channel()

        self.exchange = await self._channel.declare_exchange(
            name=settings.sorting_exchange,
            type=ExchangeType.DIRECT,
            durable=True,
        )

        queue = await self._channel.declare_queue(
            name=settings.queue_name,
            durable=True,
            arguments={"x-dead-letter-exchange": settings.retry_exchange},
        )

        for version in settings.supported_message_versions:
            for routing_key in ROUTING_KEYS:
                await queue.bind(
                    self.exchange,
                    f"{settings.routing_prefix}.{version}.{routing_key}",
                )

    async def shutdown(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        if self._channel and not self._channel.is_closed:
            await self._channel.close()

    async def publish(
        self, message: bytes, routing_key: str, content_type: str = "application/json"
    ) -> None:
        if not self._channel or self._connection.is_closed:
            raise Exception("Соединение или канал недоступны")

        await self.exchange.publish(
            aio_pika.Message(
                body=message,
                timestamp=datetime.now(),
                content_encoding="utf-8",
                content_type=content_type,
            ),
            routing_key=routing_key,
        )

    async def publish_notifications(self, messages: list[dict], batch_size: int = 100):
        for i in range(0, len(messages), batch_size):
            batch = messages[i : i + batch_size]
            for message in batch:
                await self.publish(
                    message=json.dumps(message).encode(),
                    routing_key=f"{settings.routing_prefix}.{settings.supported_message_versions[0]}.{settings.subscription_continuing_key}",
                )
