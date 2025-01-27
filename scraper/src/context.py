import os

from databases import Database
from faststream import ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker
from shared.db import (
    InboxRepository,
    IntervalRepository,
    PgRepository,
    SourceRepository,
    create_db_string,
)
from shared.entities.scraper import Channel, Folder, ProcessedIntervals, Source
from shared.handlers import error_handler
from shared.models.scraper import ScrapeRequest
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH
from telethon import TelegramClient
from telethon.sessions import StringSession

import config
from exporters import init_exporters

WORKER_ID = os.environ.get("WORKER_ID", "unknown")
KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka")

exc_middleware = ExceptionMiddleware()
broker = KafkaBroker(KAFKA_HOST, middlewares=[exc_middleware])

app = FastStream(broker)

exc_middleware.add_handler(Exception, publish=True)(error_handler)


class Context:
    def __init__(self):
        self.config = config.Config()  # pyright: ignore
        self.creds = self.config.telegram
        self.client = TelegramClient(
            StringSession(self.creds.session),
            self.creds.api_id,  # pyright: ignore
            self.creds.api_hash,
            system_version="4.16.30-vxCUSTOM",
        )
        self.shared_settings = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )
        self.pg = Database(
            create_db_string(self.config.database),
        )
        self.folder_repository = PgRepository(self.pg, Folder)
        self.source_repository = SourceRepository(self.pg, Source)
        self.channel_repository = PgRepository(self.pg, Channel)
        self.intervals_repository = IntervalRepository(
            self.pg, ProcessedIntervals
        )
        self.inbox_repository = InboxRepository(self.pg, ScrapeRequest)

    async def init_db(self):
        await self.pg.connect()

    async def dispose_db(self):
        await self.pg.disconnect()

    def init_exporters(self):
        self.exporters = init_exporters(self.config.exporters)


ctx = Context()
