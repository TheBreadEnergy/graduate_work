from abc import ABC, abstractmethod

from src.core.logging import setup_logger


class AbstractKafkaClient(ABC):
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def create_topics(self):
        ...

    @abstractmethod
    def consume_messages(self):
        ...


class MessageBrokerABC(ABC):
    @abstractmethod
    async def startup(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...

    @abstractmethod
    async def publish(
        self, message: bytes, routing_key: str, content_type: str
    ) -> None:
        ...
