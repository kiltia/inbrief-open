import logging
from contextvars import ContextVar

import torch
from databases import Database
from shared.db import PgRepository, create_db_string
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH

import config
from embeddings import init_embedders
from entities import SourceEmbeddings
from providers import init_providers

logger = logging.getLogger("embedder")

correlation_id = ContextVar("correlation_id", default="-")


class Context:
    def __init__(self):
        self.config = config.Config()  # pyright: ignore
        self.shared_settings = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )
        self.pg = Database(
            create_db_string(self.config.database),
        )
        self.embeddings_repo = PgRepository(self.pg, SourceEmbeddings)
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

    def init_providers(self):
        self.providers = init_providers(self.config.providers)


ctx = Context()
