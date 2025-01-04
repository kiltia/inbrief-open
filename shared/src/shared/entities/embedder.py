from shared.entities.common import Entity
from uuid import UUID
from typing import ClassVar


class SourceEmbeddings(Entity):
    source_id: UUID
    embedder: str
    embedding: list[float]

    _table_name: ClassVar[str] = "embeddings"
