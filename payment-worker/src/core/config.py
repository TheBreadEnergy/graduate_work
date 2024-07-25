from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")

    database_conn: PostgresDsn = Field(
        "postgresql+asyncpg://app:123qwe@localhost:5432/payments",
        alias="DATABASE_CONN",
        env="DATABASE_CONN",
    )
    echo: bool = Field(False, alias="ECHO")

    kafka_broker_host: str = Field("109.71.244.113:9094", alias="KAFKA_BROKER_HOST")
    worker_id: str = Field("worker-0", alias="WORKER_ID", env="WORKER_ID")

    payment_success_topic: str = Field("payment.success", alias="PAYMENT_SUCCESS_TOPIC")
    payment_cancelled_topic: str = Field(
        "payment.cancelled", alias="PAYMENT_CANCELLED_TOPIC"
    )

    refund_success_topic: str = Field("refund.success", alias="REFUND_SUCCESS_TOPIC")
    refund_cancelled_topic: str = Field(
        "refund.cancelled", alias="REFUND_CANCELLED_TOPIC"
    )

    num_partitions: int = Field(3, alias="NUM_PARTITIONS", env="NUM_PARTITIONS")
    replication_factor: int = Field(
        3, alias="REPLICATION_FACTOR", env="REPLICATION_FACTOR"
    )

    rabbit_login: str = Field("admin", alias="RABBIT_LOGIN", env="RABBIT_LOGIN")
    rabbit_password: str = Field(
        "password", alias="RABBIT_PASSWORD", env="RABBIT_PASSWORD"
    )
    rabbit_host: str = Field("localhost", alias="RABBIT_HOST", env="RABBIT_HOST")
    rabbit_port: int = Field(5672, alias="RABBIT_PORT", env="RABBIT_PORT")

    routing_prefix: str = Field(
        "workers", alias="MESSAGE_VERSION", env="MESSAGE_VERSION"
    )
    supported_message_versions: list[str] = ["v1"]

    retry_exchange: str = Field("workers-exchange-retry", alias="RETRY_EXCHANGE")
    sorting_exchange: str = Field(
        "workers-exchange-sorting", alias="SORTING_EXCHANGE", env="SORTING_EXCHANGE"
    )

    queue_name: str = Field("workers", alias="QUEUE_NAME", env="QUEUE_NAME")

    payment_success_key: str = Field(
        "payment-success",
        alias="PAYMENT_SUCCESS_ROUTING_KEY",
        env="PAYMENT_SUCCESS_ROUTING_KEY",
    )
    payment_cancelled_key: str = Field(
        "payment-cancelled",
        alias="PAYMENT_CANCELLED_ROUTING_KEY",
        env="PAYMENT_CANCELLED_ROUTING_KEY",
    )
    refund_success_key: str = Field(
        "refund-success",
        alias="REFUND_SUCCESS_ROUTING_KEY",
        env="REFUND_SUCCESS_ROUTING_KEY",
    )
    refund_cancelled_key: str = Field(
        "refund-cancelled",
        alias="REFUND_CANCELLED_ROUTING_KEY",
        env="REFUND_CANCELLED_ROUTING_KEY",
    )


settings = Settings()
TOPICS = (
    settings.payment_success_topic,
    settings.payment_cancelled_topic,
    settings.refund_success_topic,
)
ROUTING_KEYS = (
    settings.payment_success_key,
    settings.payment_cancelled_key,
    settings.refund_success_key,
    settings.refund_cancelled_key,
)
