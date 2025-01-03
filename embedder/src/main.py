import json
import logging
import os
import traceback

import faststream
import torch
from databases import Database
from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker, KafkaMessage
from pydantic import TypeAdapter
from shared.db import PgRepository, create_db_string
from shared.logger import configure_logging
from shared.models.api import ResponseState
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH

import config
from embeddings import init_embedders
from entities import SourceEmbeddings
from models import (
    EmbeddingResponse,
    ResponsePayload,
    ScrapeResponse,
)
from providers import init_providers

KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka")

exc_middleware = ExceptionMiddleware()
broker = KafkaBroker(KAFKA_HOST, middlewares=[exc_middleware])
app = FastStream(broker)


@exc_middleware.add_handler(Exception, publish=True)
def error_handler(exc, message=faststream.Context()):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(tb)
    return {
        "state": ResponseState.FAILED,
        "request_id": message.headers.get("request_id"),
        "error": str(exc),
        "error_repr": repr(exc),
    }


logger = logging.getLogger("embedder")


@app.on_startup
async def startup(context: ContextRepo):
    configure_logging()
    await ctx.init_db()
    ctx.init_embedders()
    ctx.init_providers()


@app.on_shutdown
async def shutdown(context: ContextRepo):
    await ctx.dispose_db()


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


payload_adapter = TypeAdapter(ResponsePayload)


@broker.publisher("inbrief.embedder.out.json")
@broker.subscriber(
    "inbrief.scraper.out.json", group_id="embedder", auto_commit=False
)
async def embedder_consumer(
    request: ScrapeResponse,
    msg: KafkaMessage,
) -> EmbeddingResponse:
    embedders = ctx.embedders

    payload = ctx.providers[0].get(request.request_id).decode("utf-8")

    payload = payload_adapter.validate_python(json.loads(payload))

    logger.debug(f"Got {len(payload.gathered)} sources")
    for embedder in embedders:
        embs = embedder.get_embeddings(map(lambda x: x.text, payload.gathered))

        entities = list(
            map(
                lambda x: SourceEmbeddings(  # pyright: ignore
                    source_id=x[0].source_id,
                    channel_id=x[0].channel_id,
                    embedder=embedder.get_label(),
                    embedding=x[1],
                ),
                zip(payload.gathered, embs, strict=True),
            )
        )

        await ctx.embeddings_repo.add(entities, ignore_conflict=True)

    await msg.ack()

    return EmbeddingResponse(
        request_id=request.request_id,
        state=ResponseState.SUCCESS,
    )
