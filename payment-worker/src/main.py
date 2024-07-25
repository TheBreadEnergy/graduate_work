from broker.kafka_client import KafkaClient
from core.config import TOPICS, settings

if __name__ == "__main__":
    kafka_client = KafkaClient(
        bootstrap_servers=settings.kafka_broker_host,
        client_id=settings.worker_id,
        topic_names=TOPICS,
    )
    kafka_client.create_topics()
    kafka_client.consume_messages()
