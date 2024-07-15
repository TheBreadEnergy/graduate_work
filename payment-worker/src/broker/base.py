from abc import ABC, abstractmethod

from core.logging import setup_logger


class AbstractKafkaClient(ABC):
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def create_topics(self):
        ...

    @abstractmethod
    def consume_messages(self):
        ...
