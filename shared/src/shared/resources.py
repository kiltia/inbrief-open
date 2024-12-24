# NOTE(nrydanov): Probably, this file doesn't have proper name for its content

from typing import Dict, List

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from .models.settings import JSONSettings


class ComponentSettings(BaseModel):
    embedders: List[str]


class Ranking(BaseModel):
    weights: Dict[str, float]


class Configuration(BaseModel):
    category_async_pool_size: int
    summarize_async_pool_size: int
    short_ops_timeout: int
    long_ops_timeout: int
    ranking: Ranking


class SharedResources(JSONSettings):
    components: ComponentSettings
    config: Configuration

    def __init__(self, path: str):
        super().__init__(path)


class EnvironmentSettings(BaseSettings):
    pass
