from aiokafka import AIOKafkaProducer

kafka_client: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    print(kafka_client)
    return kafka_client
