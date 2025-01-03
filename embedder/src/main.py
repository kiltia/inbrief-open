import json
import logging
import os
import traceback
import uuid

import faststream
from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker, KafkaMessage
from pydantic import TypeAdapter
from shared.logger import configure_logging
from shared.models.api import ResponseState

from context import correlation_id, ctx
from entities import SourceEmbeddings
from models import (
    EmbeddingResponse,
    ResponsePayload,
    ScrapeResponse,
)

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
async def startup(_: ContextRepo):
    configure_logging()
    await ctx.init_db()
    ctx.init_embedders()
    ctx.init_providers()


@app.on_shutdown
async def shutdown(_: ContextRepo):
    await ctx.dispose_db()


payload_adapter = TypeAdapter(ResponsePayload)


@broker.publisher("inbrief.embedder.out.json")
@broker.subscriber(
    "inbrief.scraper.out.json", group_id="embedder", auto_commit=False
)
async def embedder_consumer(
    request: ScrapeResponse,
    msg: KafkaMessage,
    request_id: uuid.UUID = faststream.Header("correlation_id"),
) -> EmbeddingResponse:
    embedders = ctx.embedders

    correlation_id.set(str(request_id))

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
