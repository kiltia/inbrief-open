import traceback

from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from openai import APIError


async def openai_exception_handler(_: Request, exc: APIError):
    error_type = type(exc).__name__
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "status_code": exc.status_code,
            "error_type": error_type,
            "error": exc.body["message"],
        },
    )


async def unexpected_exception_handler(_: Request, exc: Exception):
    error_type = type(exc).__name__
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_type": error_type,
            "error": repr(exc),
            "debug": traceback.format_exception(exc),
        },
    )
