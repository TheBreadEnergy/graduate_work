import json
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.encoders import jsonable_encoder
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
from src.producers.producer import ProducerABC
from src.services.event_handler import KafkaEventHandler


@pytest.mark.asyncio
async def test_payment_created_event():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = PaymentCreatedEvent(payment_id=mock_id, user_id=mock_id, license_id=mock_id)
    await event_handler.handle_payment_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.payment_created_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )


@pytest.mark.asyncio
async def test_payment_success_event():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = PaymentSuccessEvent(payment_id=mock_id)
    await event_handler.handle_payment_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.payment_success_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )


@pytest.mark.asyncio
async def test_payment_failed_event():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = PaymentCancelledEvent(payment_id=mock_id, reason="")
    await event_handler.handle_payment_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.payment_cancelled_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )


@pytest.mark.asyncio
async def test_refund_created():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = RefundCreatedEvent(refund_id=mock_id, user_id=mock_id)
    await event_handler.handle_refund_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.refund_created_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )


@pytest.mark.asyncio
async def test_refund_success():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = RefundSuccessEvent(refund_id=mock_id)
    await event_handler.handle_refund_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.refund_success_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )


@pytest.mark.asyncio
async def test_refund_failed():
    mock_id = uuid.uuid4()
    producer = MagicMock(spec=ProducerABC)
    producer.send = AsyncMock()
    event_handler = KafkaEventHandler(kafka_producer=producer)
    event = RefundCancelledEvent(refund_id=mock_id, reason="")
    await event_handler.handle_refund_event(event)
    producer.send.assert_awaited_once_with(
        topic=settings.refund_cancelled_topic,
        message=json.dumps(jsonable_encoder(event)).encode(),
        key=str(mock_id).encode(),
    )
