from broker.client import KafkaClient
from core.config import settings

if __name__ == "__main__":
    kafka_client = KafkaClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.worker_id,
        topic_names=settings.topic_names,
    )
    kafka_client.create_topics()
    kafka_client.consume_messages()
