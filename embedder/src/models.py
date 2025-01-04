from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from shared.entities.embedder import SourceEmbeddings
from shared.entities.scraper import Source
from shared.models.api import ErrorMessage
from shared.models.embedder import EmbedderSuccess

EmbedderResponse = Union[EmbedderSuccess, ErrorMessage]


class ResponsePayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    gathered: list[Source]
    cached: list[Source]


class ExportedSource(BaseModel):
    source_id: UUID
    channel_id: int
    text: str
    ts: datetime
    reference: str
    comments: list | None = None
    reactions: str | None = None
    views: int
    embeddings: dict[str, list[float]]

    @classmethod
    def _from(
        cls, origin: Source, entities: list[SourceEmbeddings]
    ) -> "ExportedSource":
        embeddings = {}

        for entity in entities:
            if entity.embedder not in embeddings:
                embeddings[entity.embedder] = []
            embeddings[entity.embedder] = entity.embedding

        return cls(
            source_id=origin.source_id,
            channel_id=origin.channel_id,
            text=origin.text,
            ts=origin.ts,
            reference=origin.reference,
            comments=origin.comments,
            reactions=origin.reactions,
            views=origin.views,
            embeddings=embeddings,
        )
