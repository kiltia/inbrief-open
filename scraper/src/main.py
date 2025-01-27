import asyncio
import logging
import os
import uuid

import faststream
from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker
from shared.entities.scraper import ScrapeTask
from shared.handlers import error_handler
from shared.logger import configure_logging
from shared.models.api import ResponseState
from shared.models.scraper import BaseResponse

from context import ctx
from executor import task_executor
from models import (
    ScrapeRequest,
)
from utils import correlation_id

KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka")

exc_middleware = ExceptionMiddleware()
broker = KafkaBroker(KAFKA_HOST, middlewares=[exc_middleware])
app = FastStream(broker)

logger = logging.getLogger("scraper")


exc_middleware.add_handler(Exception, publish=True)(error_handler)


@app.on_startup
async def startup(_: ContextRepo):
    configure_logging()
    logger.info("Started initializing scraper")
    ctx.init_exporters()
    await ctx.init_db()
    await ctx.client.start()  # type: ignore
    asyncio.create_task(task_executor())


@app.on_shutdown
async def shutdown(_: ContextRepo):
    ctx.client.disconnect()
    await ctx.dispose_db()


@broker.publisher("inbrief.events.json")
@broker.subscriber("inbrief.scraper.in.json", group_id="scraper")
async def scraper_consumer(
    request: ScrapeRequest,
    request_id: uuid.UUID = faststream.Header("correlation_id"),
) -> BaseResponse:
    correlation_id.set(request_id)
    logger.info("Started serving scrapping request")

    logger.debug("Persisting incoming scrape request")

    await ctx.inbox_repository.add(
        ScrapeTask(request_id=request_id, **request.model_dump())
    )

    logger.debug("Successfully persisted incoming scrape request")

    return BaseResponse(state=ResponseState.ACCEPTED, request_id=request_id)
