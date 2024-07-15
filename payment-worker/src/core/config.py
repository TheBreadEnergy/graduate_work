from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")

    kafka_bootstrap_servers: str = Field(
        "localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS", env="KAFKA_BOOTSTRAP_SERVERS"
    )
    worker_id: str = Field("worker-0", alias="WORKER_ID", env="WORKER_ID")


settings = Settings()
