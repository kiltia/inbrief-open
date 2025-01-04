from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.db import DatabaseConfig


class RedisConfig(BaseModel):
    host: str
    port: int


class JsonConfig(BaseModel):
    path: str


class ConnectorConfig(BaseModel):
    required_importer: str
    required_exporters: list[str]
    redis: RedisConfig
    json_config: JsonConfig = Field(alias="json")


class EmbedderConfig(BaseModel):
    required_embedders: list[str]


class KafkaConfig(BaseModel):
    session_timeout_ms: int = 1200 * 1000


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    database: DatabaseConfig
    connectors: ConnectorConfig
    embedders: EmbedderConfig
    kafka: KafkaConfig
