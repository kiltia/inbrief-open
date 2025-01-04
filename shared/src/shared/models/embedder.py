from enum import Enum
from shared.models.api import BaseResponse


class EmbeddingSource(str, Enum):
    JINA = "jina"


class EmbedderSuccess(BaseResponse):
    pass
