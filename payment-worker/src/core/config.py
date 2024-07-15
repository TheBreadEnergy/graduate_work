from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")

    kafka_bootstrap_servers: str = Field(
        "localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS", env="KAFKA_BOOTSTRAP_SERVERS"
    )
    worker_id: str = Field("worker-0", alias="WORKER_ID", env="WORKER_ID")
    topic_names: List[str] = Field(..., alias="TOPIC_NAMES", env="TOPIC_NAMES")
    num_partitions: int = Field(3, alias="NUM_PARTITIONS", env="NUM_PARTITIONS")
    replication_factor: int = Field(
        3, alias="REPLICATION_FACTOR", env="REPLICATION_FACTOR"
    )


settings = Settings()
