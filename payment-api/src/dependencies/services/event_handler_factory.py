from functools import cache

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.postgres import get_session
from src.dependencies.registrator import add_factory_to_mapper
from src.producers.kafka import get_producer
from src.producers.producer import KafkaProducer
from src.services.billing.event_processor import (
    BillingEventProcessorABC,
    YookassaBillingEventProcessor,
)
from src.services.event_handler import EventHandlerABC, KafkaEventHandler
from src.services.uow import SqlAlchemyUnitOfWork


@add_factory_to_mapper(EventHandlerABC)
@cache
def create_event_handler(
    producer: AIOKafkaProducer = Depends(get_producer),
) -> KafkaEventHandler:
    return KafkaEventHandler(kafka_producer=KafkaProducer(producer=producer))


@add_factory_to_mapper(BillingEventProcessorABC)
@cache
def create_billing_event_handler(
    event_handler: EventHandlerABC = Depends(),
    session: AsyncSession = Depends(get_session),
) -> YookassaBillingEventProcessor:
    return YookassaBillingEventProcessor(
        event_handler=event_handler, uow=SqlAlchemyUnitOfWork(session=session)
    )
