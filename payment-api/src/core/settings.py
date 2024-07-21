import backoff
import redis
import sqlalchemy.exc
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import RequestException


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")
    project_name: str = Field(
        "API для управления платежами",
        alias="PROJECT_NAME",
    )
    description: str = Field(
        "Оплата подписки, возврат средств, просмотр истории платежей и возвратов",
        alias="DESCRIPTION",
    )
    version: str = Field("1.0.0", alias="VERSION")
    debug: bool = Field(False, alias="DEBUG")
    echo: bool = Field(False, alias="ECHO")
    database_conn: PostgresDsn = Field(
        "postgresql+asyncpg://app:123qwe@localhost:5432/payments",
        alias="DATABASE_CONN",
    )
    cache_host: str = Field("localhost", alias="CACHE_HOST")
    cache_port: int = Field(6379, alias="CACHE_PORT")
    jaeger_service: str = Field("localhost:4317", alias="JAEGER_SERVICE")
    auth_service: str = Field("localhost:50051", alias="AUTH_SERVICE")
    redirect_url: str = Field("/", alias="REDIRECT_URL")
    shop_url: str = Field("414721", alias="SHOP_URL")
    shop_secret: str = Field(
        "test_AA4Yd_1RptIPfh9DKeBakY6pTuYqJe3LuJ1STg0iNKI", alias="SHOP_SECRET"
    )
    subscription_address: str = Field("localhost:50051", alias="SUBSCRIPTION_ADDRESS")
    payment_created_topic: str = Field("payment.created", alias="PAYMENT_CREATED_TOPIC")
    payment_cancelled_topic: str = Field(
        "payment.cancelled", alias="PAYMENT_CANCELLED_TOPIC"
    )
    payment_success_topic: str = Field("payment.success", alias="PAYMENT_SUCCESS_TOPIC")
    refund_created_topic: str = Field("refund.created", alias="REFUND_CREATED_TOPIC")
    refund_cancelled_topic: str = Field(
        "refund.cancelled", alias="REFUND_CANCELLED_TOPIC"
    )
    kafka_broker_host: str = Field("109.71.244.113:9094", alias="KAFKA_BROKER_HOST")
    auto_offset_reset: str = Field("earliest", alias="AUTO_OFFSET_RESET")
    ENABLE_AUTO_COMMIT: bool = Field(False, alias="ENABLE_AUTO_COMMIT")
    refund_success_topic: str = Field("refund.success", alias="REFUND_SUCCESS_TOPIC")
    backoff_max_retries: int = Field(3, alias="BACKOFF_MAX_RETRIES")
    retry_backoff_ms: int = Field(500, alias="RETRY_BACKOFF_MS")
    capture: bool = Field(True, alias="CAPTURE_PAYMENT")
    jwt_secret: str = Field("secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", alias="JWT_METHOD")
    grpc_port: int = Field(50051, alias="GRPC_PORT")


settings = Settings()


BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": (
        RequestException,
        sqlalchemy.exc.DisconnectionError,
        redis.ConnectionError,
        redis.TimeoutError,
    ),
    "max_tries": settings.backoff_max_retries,
}
