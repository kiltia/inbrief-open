import asyncio
import logging
import uuid

import faststream
from faststream import ContextRepo
from shared.entities.scraper import ScrapeTask
from shared.logger import configure_logging
from shared.models.api import ResponseState
from shared.models.scraper import BaseResponse

from context import app, broker, ctx
from executor import task_executor
from models import (
    ScrapeRequest,
)
from utils import correlation_id

logger = logging.getLogger("scraper")


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
@broker.subscriber("inbrief.scraper.in.json", group_id="scraper-group")
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
