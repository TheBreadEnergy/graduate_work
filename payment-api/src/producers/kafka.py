from aiokafka import AIOKafkaProducer

kafka_client: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    return kafka_client
