import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from matcher import Matcher
from pydantic import TypeAdapter

from shared.exceptions import unexpected_exception_handler
from shared.logger import configure_logging
from shared.models import LinkingRequest, LinkingResponse
from shared.routes import LinkerRoutes


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware, validator=None)

app.add_exception_handler(Exception, unexpected_exception_handler)


logger = logging.getLogger("linker")


@app.post(LinkerRoutes.GET_STORIES)
async def get_stories(request: LinkingRequest) -> LinkingResponse:
    logger.info("Started serving linker request")
    matcher = Matcher(
        request.entries,
        request.config.embedding_source,
        request.config.scorer,
        request.config.metric,
    )

    results, embeddings = matcher.get_stories(
        method_name=request.config.method,
        **request.settings,
        return_plot_data=request.return_plot_data,
    )

    adapter = TypeAdapter(LinkingResponse)
    if request.return_plot_data:
        return adapter.validate_python(
            {"results": results, "embeddings": embeddings.tolist()}
        )
    else:
        return adapter.validate_python({"results": results})


@app.get("/")
def hello_world():
    return "Linker API is running!"
