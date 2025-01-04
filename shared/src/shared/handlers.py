import faststream
import traceback
from shared.models.api import ResponseState


def error_handler(exc, message=faststream.Context(), logger=faststream.Context()):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(tb)
    return {
        "state": ResponseState.FAILED,
        "request_id": message.headers.get("request_id"),
        "error": str(exc),
        "error_repr": repr(exc),
    }
