from functools import cache

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from src.dependencies.registrator import add_factory_to_mapper
from src.producers.kafka import get_producer
from src.services.event_handler import EventHandlerABC, KafkaEventHandler


@add_factory_to_mapper(EventHandlerABC)
@cache
def create_event_handler(
    producer: AIOKafkaProducer = Depends(get_producer),
) -> KafkaEventHandler:
    return KafkaEventHandler(kafka_producer=producer)
