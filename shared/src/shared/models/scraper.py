from datetime import datetime
from enum import Enum

from optional import Optional
from pydantic import BaseModel

from .request import BaseRequest, BaseResponse


class ScrapeRequest(BaseRequest):
    chat_folder_link: str = "https://t.me/addlist/W9JQ42l78Kc5MTAy"
    offset_date: Optional[datetime.datetime] = None
    end_date: datetime.datetime
    social: bool = False
    exporters: list[str] = []


class SourceOutput(BaseModel):
    source_id: int
    text: str
    ts: datetime.datetime
    channel_id: int
    reference: str
    label: str | None = None
    comments: list | None = None
    reactions: str | None = None
    views: int


class ScrapeAction(str, Enum):
    FULL_SCAN = "full_scan"
    PARTIAL_SCAN = "partial_scan"
    CACHED = "cached"
    FAILED = "fail"


class ScrapeInfo(BaseModel):
    action: ScrapeAction
    count: int


class ScrapeResponse(BaseResponse):
    actions: dict[int, ScrapeInfo]
