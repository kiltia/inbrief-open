from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from typing import Annotated, Union

from shared.models.api import BaseRequest, BaseResponse, ErrorMessage
from shared.entities.scraper import Source


class ScrapeRequest(BaseRequest):
    chat_folder_link: str = "https://t.me/addlist/W9JQ42l78Kc5MTAy"
    right_bound: Annotated[
        datetime, Field(default_factory=lambda _: datetime.now().astimezone())
    ]
    left_bound: datetime
    social: bool = False
    exporters: list[str] = []


class ScrapeAction(str, Enum):
    FULL_SCAN = "full_scan"
    PARTIAL_SCAN = "partial_scan"
    CACHED = "cached"
    FAILED = "fail"


class ScrapeInfo(BaseModel):
    action: ScrapeAction
    count: int


class ScrapeSuccess(BaseResponse):
    actions: dict[int, ScrapeInfo]


ScrapeResponse = Union[ScrapeSuccess, ErrorMessage]


class ResponsePayload(BaseModel):
    cached: list[Source]
    gathered: list[Source]
