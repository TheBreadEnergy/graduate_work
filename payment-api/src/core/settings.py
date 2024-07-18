from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        "postgresql+asyncpg://app:123@qwe@localhost:5432/payments",
        alias="DATABASE_CONN",
    )
    cache_host: str = Field("localhost", alias="CACHE_HOST")
    cache_port: int = Field(6379, alias="CACHE_PORT")
    jaeger_service: str = Field("localhost:4317", alias="JAEGER_SERVICE")
    auth_service: str = Field("localhost:50051", alias="AUTH_SERVICE")
    redirect_url: str = Field("", alias="REDIRECT_URL")
    shop_url: str = Field("", alias="SHOP_URL")
    shop_secret: str = Field("", alias="SHOP_SECRET")
    subscription_address: str = Field("localhost:50051", alias="SUBSCRIPTION_ADDRESS")


settings = Settings()
