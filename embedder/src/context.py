import logging
import os

import torch
from databases import Database
from faststream import ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker
from shared.db import EmbeddingRepository, InboxRepository, create_db_string
from shared.entities.embedder import EmbeddingTask, SourceEmbeddings
from shared.handlers import error_handler
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH

import config
from connectors import init_connectors
from embeddings import init_embedders

logger = logging.getLogger("embedder")

WORKER_ID = os.environ.get("WORKER_ID", "worker-0")
KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka")

exc_middleware = ExceptionMiddleware()
broker = KafkaBroker(KAFKA_HOST, middlewares=[exc_middleware])
app = FastStream(broker)


exc_middleware.add_handler(Exception, publish=True)(error_handler)


class Context:
    def __init__(self):
        self.config = config.Config()  # pyright: ignore
        self.shared_settings = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )
        self.pg = Database(
            create_db_string(self.config.database),
        )
        self.embeddings_repo = EmbeddingRepository(self.pg, SourceEmbeddings)
        self.inbox_repository = InboxRepository(self.pg, EmbeddingTask)
        self.embedders = []

    async def init_db(self):
        await self.pg.connect()

    async def dispose_db(self):
        await self.pg.disconnect()

    def init_embedders(self):
        cuda_available = torch.cuda.is_available()
        mps_available = torch.backends.mps.is_available()
        logger.info("Initializing embedding functionality")
        logger.info(
            "Checking cuda availability: %s",
            cuda_available,
        )
        logger.info(
            "Checking mps availability: %s",
            mps_available,
        )
        device = (
            torch.device("mps")
            if mps_available
            else torch.device("cuda")
            if cuda_available
            else torch.device("cpu")
        )
        logger.info("Using device: %s", device)

        self.embedders = init_embedders(
            self.config.embedders.required_embedders, device
        )

    def init_connectors(self):
        self.connectors = init_connectors(self.config.connectors)


ctx = Context()
