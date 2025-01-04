from shared.entities.common import Entity
from pydantic import Field
from uuid import UUID
from datetime import datetime
from typing import ClassVar
from shared.utils import correlation_id


class Source(Entity):
    source_id: UUID
    text: str
    ts: datetime
    channel_id: int
    reference: str
    comments: list | None = None
    reactions: str | None = None
    views: int
    request_id: UUID = Field(default_factory=correlation_id.get)

    _table_name: ClassVar[str] = "source"
    _pk: ClassVar[str] = "source_id"


class Channel(Entity):
    channel_id: int
    title: str
    about: str
    subscribers: int

    _table_name: ClassVar[str] = "channel"
    _pk: ClassVar[str] = "channel_id"


class ProcessedIntervals(Entity):
    l_bound: datetime
    r_bound: datetime
    request_id: UUID
    channel_id: int

    _table_name: ClassVar[str] = "processed_intervals"
    _pk: ClassVar[str] = "request_id"


class Folder(Entity):
    chat_folder_link: str
    channels: list[int]

    _table_name: ClassVar[str] = "folder"
    _pk: ClassVar[str] = "chat_folder_link"
