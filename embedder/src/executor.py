import asyncio
import json
import logging

from pydantic import TypeAdapter
from shared.entities.embedder import EmbeddingTask, SourceEmbeddings

from connectors import get_connector
from context import WORKER_ID, broker, ctx
from models import (
    ErrorMessage,
    ExportedSource,
    ResponsePayload,
)

payload_adapter = TypeAdapter(ResponsePayload)

logger = logging.getLogger("embedder")

task_adapter = TypeAdapter(EmbeddingTask)

embeddings_adapter = TypeAdapter(list[SourceEmbeddings])


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

        # await broker.publish(
        #     topic="inbrief.embedder.in",
        #     message="",
        #     headers={"correlation_id": str(task.request_id)},
        # )


async def execute_task(task: EmbeddingTask):
    embedders = ctx.embedders
    if isinstance(task, ErrorMessage):
        return task

    importer = get_connector(
        ctx.config.connectors.required_importer, ctx.connectors
    )
    payload = importer.import_from(task.request_id).decode("utf-8")

    payload = payload_adapter.validate_python(json.loads(payload))

    logger.debug(f"Got {len(payload)} sources")
    embeddings = {}
    for embedder in embedders:
        embs = embedder.get_embeddings(
            map(lambda x: f"separation:{x.text}", payload),
            truncate_dim=128,
        )

        entities = list(
            map(
                lambda x: SourceEmbeddings(  # pyright: ignore
                    source_id=x[0].source_id,
                    embedder=embedder.get_label(),
                    embedding=x[1],
                ),
                zip(payload, embs, strict=True),
            )
        )

        embeddings[embedder.get_label()] = embs
        await ctx.embeddings_repo.add(entities, ignore_conflict=True)

    if len(ctx.config.connectors.required_exporters) > 0:
        ids = set(list(map(lambda x: x.source_id, payload)))

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
                payload,
            )
        )

        for exporter in ctx.config.connectors.required_exporters:
            connector = get_connector(exporter, ctx.connectors)
            connector.export(
                task.request_id,
                json.dumps(
                    list(map(lambda x: x.model_dump(), exported_sources)),
                    default=str,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
            )
