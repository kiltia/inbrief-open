import json
import logging
import os
import uuid

import faststream
from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker, KafkaMessage
from pydantic import TypeAdapter
from shared.entities.embedder import SourceEmbeddings
from shared.handlers import error_handler
from shared.logger import configure_logging
from shared.models.api import ResponseState
from shared.models.embedder import EmbedderSuccess
from shared.models.scraper import ScrapeResponse

from connectors import get_connector
from context import ctx
from models import (
    EmbedderResponse,
    ErrorMessage,
    ExportedSource,
    ResponsePayload,
)
from utils import correlation_id

KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka")

exc_middleware = ExceptionMiddleware()
broker = KafkaBroker(KAFKA_HOST, middlewares=[exc_middleware])
app = FastStream(broker)


exc_middleware.add_handler(Exception, publish=True)(error_handler)


logger = logging.getLogger("embedder")


@app.on_startup
async def startup(_: ContextRepo):
    configure_logging()
    await ctx.init_db()
    ctx.init_embedders()
    ctx.init_connectors()


@app.on_shutdown
async def shutdown(_: ContextRepo):
    await ctx.dispose_db()


payload_adapter = TypeAdapter(ResponsePayload)
embeddings_adapter = TypeAdapter(list[SourceEmbeddings])


@broker.publisher("inbrief.embedder.out.json")
@broker.subscriber(
    "inbrief.scraper.out.json",
    group_id="embedder",
    auto_commit=False,
    session_timeout_ms=ctx.config.kafka.session_timeout_ms,
)
async def embedder_consumer(
    message: ScrapeResponse,
    msg: KafkaMessage,
    request_id: uuid.UUID = faststream.Header("correlation_id"),
) -> EmbedderResponse:
    embedders = ctx.embedders

    correlation_id.set(str(request_id))

    if isinstance(message, ErrorMessage):
        return message

    importer = get_connector(
        ctx.config.connectors.required_importer, ctx.connectors
    )
    payload = importer.import_from(message.request_id).decode("utf-8")

    payload = payload_adapter.validate_python(json.loads(payload))

    logger.debug(f"Got {len(payload.gathered)} sources")
    embeddings = {}
    for embedder in embedders:
        embs = embedder.get_embeddings(
            map(lambda x: f"separation:{x.text}", payload.gathered),
            truncate_dim=128,
        )

        entities = list(
            map(
                lambda x: SourceEmbeddings(  # pyright: ignore
                    source_id=x[0].source_id,
                    embedder=embedder.get_label(),
                    embedding=x[1],
                ),
                zip(payload.gathered, embs, strict=True),
            )
        )

        embeddings[embedder.get_label()] = embs
        await ctx.embeddings_repo.add(entities, ignore_conflict=True)

    if len(ctx.config.connectors.required_exporters) > 0:
        ids = set(list(map(lambda x: x.source_id, payload.gathered)))

        grouped = {}

        stored = embeddings_adapter.validate_python(
            await ctx.embeddings_repo.get_by_ids(ids)
        )

        for e in stored:
            grouped.setdefault(e.source_id, []).append(e)

        exported_sources = list(
            map(
                lambda x: ExportedSource._from(
                    x, grouped.setdefault(x.source_id, [])
                ),
                payload.gathered,
            )
        )

        for exporter in ctx.config.connectors.required_exporters:
            connector = get_connector(exporter, ctx.connectors)
            connector.export(
                request_id,
                json.dumps(
                    list(map(lambda x: x.model_dump(), exported_sources)),
                    default=str,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
            )

    await msg.ack()

    return EmbedderSuccess(
        request_id=message.request_id,
        state=ResponseState.SUCCESS,
    )
