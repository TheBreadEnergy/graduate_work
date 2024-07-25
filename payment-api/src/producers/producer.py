from abc import ABC, abstractmethod

from aiokafka import AIOKafkaProducer


class ProducerABC(ABC):
    @abstractmethod
    async def send(self, topic: str, message: bytes, key: bytes):
        ...


class KafkaProducer(ProducerABC):
    def __init__(self, producer: AIOKafkaProducer):
        self._producer = producer

    async def send(self, topic: str, message: bytes, key: bytes):
        await self._producer.send(topic=topic, value=message, key=key)
