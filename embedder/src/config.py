from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from shared.db import DatabaseConfig


class RedisConfig(BaseModel):
    host: str
    port: int


class ProviderConfig(BaseModel):
    required_providers: list[str]
    redis: RedisConfig

class EmbedderConfig(BaseModel):
    required_embedders: list[str]


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    database: DatabaseConfig
    providers: ProviderConfig
    embedders: EmbedderConfig
