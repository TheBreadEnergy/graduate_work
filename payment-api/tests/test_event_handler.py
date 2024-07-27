import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.encoders import jsonable_encoder
from src.models.events.payment import PaymentEventABC
from src.models.events.refund import RefundEventABC
from src.producers.producer import ProducerABC
from src.services.event_handler import KafkaEventHandler
from tests.testdata.events import PAYMENT_EVENTS, REFUND_EVENTS

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("event,topic", PAYMENT_EVENTS)
async def test_payment_events(event: PaymentEventABC, topic: str):

    # Arrange
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)

    # Act
    await event_handler.handle_payment_event(event)

    # Assert
    producer.send.assert_awaited_once_with(
        topic=topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(event.payment_id).encode(),
    )


@pytest.mark.parametrize("event, topic", REFUND_EVENTS)
async def test_refund_created(event: RefundEventABC, topic: str):
    # Arrange
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)

    # Act
    await event_handler.handle_refund_event(event)

    # Assert
    producer.send.assert_awaited_once_with(
        topic=topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(event.refund_id).encode(),
    )
