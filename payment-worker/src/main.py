import asyncio

from broker.kafka_client import KafkaClient
from core.config import TOPICS, settings


async def main():
    kafka_client = KafkaClient(
        bootstrap_servers=settings.kafka_broker_host,
        client_id=settings.worker_id,
        topic_names=TOPICS,
    )
    await kafka_client.consume_messages()


if __name__ == "__main__":
    asyncio.run(main())
