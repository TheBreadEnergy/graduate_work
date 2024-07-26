from abc import ABC, abstractmethod


class MessageBrokerABC(ABC):
    @abstractmethod
    async def startup(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...

    @abstractmethod
    async def publish(
        self, message: bytes, routing_key: str, content_type: str
    ) -> None: ...
