import backoff
import redis
import sqlalchemy
from aiohttp import ClientConnectorError
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.exceptions.rate_limit import RateLimitException
from src.rate.rate_limiter import is_circuit_processable


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")
    project_name: str = Field(
        "API для управления подписками",
        alias="PROJECT_NAME",
    )
    description: str = Field(
        "Просмотр подписок, удаление подписок",
        alias="DESCRIPTION",
    )
    version: str = Field("1.0.0", alias="VERSION")
    debug: bool = Field(True, alias="DEBUG")
    echo: bool = Field(True, alias="ECHO")
    database_conn: PostgresDsn = Field(
        "postgresql+asyncpg://app:123qwe@localhost:5432/subscriptions",
        alias="DATABASE_CONN",
    )
    cache_host: str = Field("localhost", alias="CACHE_HOST")
    cache_port: int = Field(6379, alias="CACHE_PORT")
    profile_endpoint: str = Field("", alias="PROFILE_ENDPOINT")
    backoff_max_retries: int = Field(3, alias="BACKOFF_MAX_RETRIES")
    retry_backoff_ms: int = Field(500, alias="RETRY_BACKOFF_MS")
    grpc_port: int = Field(50051, alias="GRPC_PORT")
    trust_env: bool = Field(True, alias="TRUST_ENV")
    enable_tracer: bool = Field(False, alias="ENABLE_TRACER")
    jaeger_agent_host: str = Field("localhost", alias="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(14250, alias="JAEGER_AGENT_PORT")


settings = Settings()


BACKOFF_CONFIG = {
    "wait_gen": backoff.expo,
    "exception": (
        ClientConnectorError,
        RateLimitException,
        sqlalchemy.exc.DisconnectionError,
        redis.ConnectionError,
        redis.TimeoutError,
    ),
    "max_tries": settings.backoff_max_retries,
}


CIRCUIT_CONFIG = {"expected_exception": is_circuit_processable}
