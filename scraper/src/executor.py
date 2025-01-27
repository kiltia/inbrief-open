import asyncio
import json
import logging

from pydantic import TypeAdapter
from shared.entities.scraper import ScrapeTask
from shared.models.api import ResponseState

from context import WORKER_ID, ctx
from models import (
    ScrapeSuccess,
)
from scraper import scrape_channels

logger = logging.getLogger("scraper")

task_adapter = TypeAdapter(ScrapeTask)


async def task_executor():
    while True:
        logger.debug("Checking for new tasks")
        async with ctx.pg.transaction():
            task = await ctx.inbox_repository.get_next(WORKER_ID)
            if task is None:
                logger.debug(
                    "No tasks found were found, retrying in 10 seconds"
                )
                await asyncio.sleep(10)
                continue

            logger.debug("Found a new task, starting execution")
            task = task_adapter.validate_python(task)
            await ctx.inbox_repository.commit_task(
                task.request_id, WORKER_ID, state="in_progress"
            )

        await execute_task(task)

        await ctx.inbox_repository.commit_task(task.request_id, WORKER_ID)


async def execute_task(task: ScrapeTask):
    request_id = task.request_id
    payload, actions = await scrape_channels(ctx, task, request_id)

    payload_json = json.dumps(
        payload.model_dump(), default=str, sort_keys=True, ensure_ascii=False
    )

    for exporter in ctx.exporters:
        logger.info(f"Exporting to {exporter.get_label()}")
        exporter.export(request_id, payload_json)

    return ScrapeSuccess(
        request_id=request_id,
        state=ResponseState.SUCCESS,
        actions=actions,
    )
