import asyncio
import json
import logging
import uuid

import faststream
from faststream import ContextRepo
from pydantic import TypeAdapter
from pydantic.json import pydantic_encoder
from shared.entities.embedder import EmbeddingTask
from shared.logger import configure_logging
from shared.models.api import BaseResponse, ResponseState
from shared.models.embedder import EmbedderSuccess

from connectors import get_connector
from context import app, broker, ctx
from executor import task_executor
from models import (
    ResponsePayload,
)
from utils import correlation_id

logger = logging.getLogger("embedder")


@app.on_startup
async def startup(_: ContextRepo):
    configure_logging()
    await ctx.init_db()
    ctx.init_embedders()
    ctx.init_connectors()
    asyncio.create_task(task_executor())


@app.on_shutdown
async def shutdown(_: ContextRepo):
    await ctx.dispose_db()


payload_adapter = TypeAdapter(ResponsePayload)


@broker.subscriber(
    "inbrief.embedder.in", group_id="embedder-group", auto_commit=False
)
@broker.publisher("inbrief.events.json")
async def embedder_consumer(
    request_id: uuid.UUID = faststream.Header("correlation_id"),
) -> BaseResponse:
    logger.debug(f"Received request {request_id}")
    correlation_id.set(str(request_id))

    importer = get_connector(
        ctx.config.connectors.required_importer, ctx.connectors
    )
    logger.debug(f"Importing request body from {request_id}")
    payload = importer.import_from(request_id).decode("utf-8")

    logger.debug(f"Got {len(payload)} sources")
    logger.debug(f"Source payload example: {payload[0]}")

    payload = payload_adapter.validate_python(json.loads(payload))

    logger.debug("Persisting request to inbox")
    await ctx.inbox_repository.add(
        EmbeddingTask(
            request_id=request_id,
            embedder="jina",
            payload=json.dumps(payload, default=pydantic_encoder),
        )
    )
    logger.debug("Successfully persisted request to inbox")

    return EmbedderSuccess(
        request_id=request_id,
        state=ResponseState.ACCEPTED,
    )
