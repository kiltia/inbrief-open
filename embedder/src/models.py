from datetime import datetime
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict
from shared.models.api import BaseResponse


class ScrapeAction(str, Enum):
    FULL_SCAN = "full_scan"
    PARTIAL_SCAN = "partial_scan"
    CACHED = "cached"
    FAILED = "fail"


class ScrapeInfo(BaseModel):
    action: ScrapeAction
    count: int


class EmbeddingSource(str, Enum):
    JINA = "jina"


class ScrapeResponse(BaseResponse):
    actions: dict[int, ScrapeInfo]


class Source(BaseModel):
    source_id: int
    text: str
    ts: datetime
    channel_id: int
    reference: str
    label: str | None = None
    comments: list | None = None
    reactions: str | None = None
    views: int

    _table_name: ClassVar[str] = "source"
    _pk: ClassVar[str] = "source_id"


class EmbeddingResponse(BaseResponse):
    pass


class ResponsePayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    gathered: list[Source]
