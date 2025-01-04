import json
import logging
import os
import uuid

import faststream
from faststream import ContextRepo, ExceptionMiddleware, FastStream
from faststream.kafka import KafkaBroker, KafkaMessage
from shared.handlers import error_handler
from shared.logger import configure_logging
from shared.models.api import ResponseState

from context import ctx
from models import (
    ScrapeRequest,
    ScrapeResponse,
    ScrapeSuccess,
)
from scraper import scrape_channels
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


@app.on_shutdown
async def shutdown(_: ContextRepo):
    ctx.client.disconnect()
    await ctx.dispose_db()


@broker.publisher("inbrief.scraper.out.json")
@broker.subscriber(
    "inbrief.scraper.in.json", auto_commit=False, group_id="scraper"
)
async def scraper_consumer(
    request: ScrapeRequest,
    msg: KafkaMessage,
    request_id: uuid.UUID = faststream.Header("correlation_id"),
) -> ScrapeResponse:
    correlation_id.set(request_id)

    logger.info("Started serving scrapping request")

    payload, actions = await scrape_channels(ctx, request, request_id)

    payload_json = json.dumps(
        payload.model_dump(), default=str, sort_keys=True, ensure_ascii=False
    )

    for exporter in ctx.exporters:
        logger.info(f"Exporting to {exporter.get_label()}")
        exporter.export(request_id, payload_json)

    await msg.ack()

    return ScrapeSuccess(
        request_id=request_id,
        state=ResponseState.SUCCESS,
        actions=actions,
    )
