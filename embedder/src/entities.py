from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Entity(BaseModel):
    created_at: Annotated[datetime, Field(default_factory=datetime.now)]


class SourceEmbeddings(Entity):
    source_id: int
    channel_id: int
    embedder: str
    embedding: list[float]

    _table_name: ClassVar[str] = "embeddings"
