from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class BaseRequest(BaseModel):
    pass


class ResponseState(str, Enum):
    SUCCESS = "success"
    ACCEPTED = "accepted"
    FAILED = "failed"


class BaseResponse(BaseModel):
    state: ResponseState
    request_id: UUID


class ErrorMessage(BaseResponse):
    error: str
    error_repr: str
