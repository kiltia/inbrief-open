from uuid import uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from fastapi import FastAPI
from matcher import Matcher

from shared.db import PgRepository, create_db_string
from shared.entities import Story, StoryPost
from shared.logger import configure_logging
from shared.models import LinkingRequest
from shared.resources import SharedResources
from shared.routes import LinkerRoutes
from shared.utils import SHARED_CONFIG_PATH

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware, validator=None)


class Context:
    def __init__(self):
        self._shared_resources = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )
        self._pg = Database(create_db_string(self._shared_resources.pg_creds))
        self.story_repository = PgRepository(self._pg, Story)

        self.story_post_repository = PgRepository(self._pg, StoryPost)

    async def init_db(self):
        await self._pg.connect()

    async def dispose_db(self):
        await self._pg.disconnect()


ctx = Context()


@app.post(LinkerRoutes.GET_STORIES)
async def get_stories(request: LinkingRequest):
    matcher = Matcher(request.text, request.embeddings, request.date)
    stories, stories_nums = matcher.get_stories(
        request.method, **request.config
    )

    uuids = [
        uuid4() for _ in range(len(stories_nums) + len(stories_nums[-1]) - 1)
    ]

    stories_uuids = [Story(story_id=i) for i in uuids]
    await ctx.story_repository.add(stories_uuids)

    stories = []
    uuid_num = 0
    for i in range(len(stories_nums[:-1])):
        for j in range(len(stories_nums[i])):
            story = StoryPost(
                story_id=uuids[uuid_num],
                source_id=request.source_id[stories_nums[i][j]],
                channel_id=request.channel_id[stories_nums[i][j]],
            )
            stories.append(story)
        uuid_num += 1
    # NOTE(sokunkov): We need to finally decide what we want to do
    # with the noisy cluster
    for i in range(len(stories_nums[-1])):
        story = StoryPost(
            story_id=uuids[uuid_num],
            source_id=request.source_id[stories_nums[-1][i]],
            channel_id=request.channel_id[stories_nums[-1][i]],
        )
        stories.append(story)
        uuid_num += 1

    await ctx.story_post_repository.add(stories)

    stories = stories_nums[:-1]
    stories.extend(stories_nums[-1])

    story_ids = list(map(lambda t: uuids[t[0]], enumerate(stories)))
    return story_ids


@app.get("/")
def hello_world():
    return "Linker API is running!"


@app.on_event("shutdown")
async def dispose():
    await ctx.dispose_db()


@app.on_event("startup")
async def main() -> None:
    configure_logging()

    await ctx.init_db()
