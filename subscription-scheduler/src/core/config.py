from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")

    database_conn: PostgresDsn = Field(
        "postgresql+asyncpg://app:123qwe@localhost:5431/subscriptions",
        alias="DATABASE_CONN",
        env="DATABASE_CONN",
    )

    echo: bool = Field(False, alias="ECHO")

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

    subscription_continuing_key: str = Field(
        "subscription-continuing",
        alias="SUBSCRIPTION_CONTINUING_KЕУ",
        env="SUBSCRIPTION_CONTINUING_KEY",
    )


settings = Settings()

ROUTING_KEYS = (settings.subscription_continuing_key,)
