import json
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel

from shared.entities import StorySources
import datetime
from typing import Optional


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config_data = json.load(f)
            return super().__init__(**config_data)

    class Config:
        populate_by_name = True


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)

    return wrapper


class PresetData(BaseModel):
    preset_name: str
    chat_folder_link: str
    editor_prompt: str

    @classmethod
    def get_fields(cls):
        return list(cls.model_fields.keys())


class EmbeddingSource(str, Enum):
    FTMLM = "ft+mlm"
    OPENAI = "open-ai"
    MLM = "mini-lm"


class ClusteringMethod(str, Enum):
    HDBSCAN = "hdbscan"
    DBSCAN = "dbscan"
    KMeans = "kmeans"
    Agglomerative = "agglomerative"
    OPTICS = "optics"
    AffinityPropagation = "affinity_propagation"
    SpectralClustering = "spectral"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@extend_enum(ClusteringMethod)
class CategoryMethod(str, Enum):
    CLASSIFIER = "classifier"


class OpenAIModels(str, Enum):
    GPT3_TURBO = "gpt-3.5-turbo-1106"
    GPT4 = "gpt-4"
    GPT4_32k = "gpt-4-32k"
    GPT4_TURBO = "gpt-4-1106-preview"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class SummaryMethod(str, Enum):
    OPENAI = "openai"
    BART = "bart"


class Density(str, Enum):
    CATEGORY = "category"
    TITLE = "title"
    SMALL = "small"
    LARGE = "large"

    def next(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        if index >= len(members):
            raise StopIteration("End of enumeration reached")
        return members[index]

    def prev(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) - 1
        if index < 0:
            raise StopIteration("Beginning of enumeration reached")
        return members[index]


class UserFeedbackValue(str, Enum):
    LIKE = "like"
    BAD_LINKAGE = "bad_linkage"
    BAD_CATEGORIZING = "bad_categorizing"
    LEXICAL_OR_GRAMMAR_ERRORS = "errors"
    FAKE_NEWS = "fake_news"
    SUMMARY_TOO_SHORT = "too_short"
    SUMMARY_TOO_LONG = "too_long"


class Config(BaseModel):
    embedding_source: EmbeddingSource
    linking_method: ClusteringMethod
    category_method: CategoryMethod
    summary_method: SummaryMethod


class BaseRequest(BaseModel):
    pass


class BaseResponse(BaseModel):
    pass


class ExternalRequest(BaseRequest):
    chat_id: int


# Scraper API


class ScrapeRequest(BaseRequest):
    channels: List[int] = [2236047183]
    required_embedders: List[str] | None = ["open-ai"]
    offset_date: Optional[datetime.datetime] = None
    end_date: datetime.datetime
    social: bool = False


class SourceOutput(BaseModel):
    source_id: int
    text: str
    date: datetime.datetime
    channel_id: int
    reference: str
    embeddings: dict
    label: str | None = None
    comments: list | None = None
    reactions: str | None = None
    views: int


class ScrapeResponse(BaseResponse):
    sources: list[SourceOutput]
    skipped_channel_ids: list[int]


class SyncRequest(BaseRequest):
    chat_folder_link: str = "https://t.me/addlist/W9JQ42l78Kc5MTAy"


# Linker API


class LinkingScorer(str, Enum):
    SILHOUETTE = "silhouette"
    CALINSKI_HARABASZ = "calinski_harabasz"
    WEIGHTED_SCORER = "weighted_scorer"
    BUSINESS_SCORER = "business_scorer"


class DistancesMetric(str, Enum):
    CITYBLOCK = "cityblock"
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


class Entry(BaseModel):
    text: str
    embeddings: dict[str, list[float]]


StoriesNums = list[list[int]]
Embeddings = list[list[float]]


class ClusteringMetadata(BaseModel):
    score: float
    config: dict


class ClusteringEntry(BaseModel):
    metadata: ClusteringMetadata | None = None
    stories_nums: StoriesNums


class PlotData(BaseModel):
    payload: list[StorySources]
    results: list[ClusteringEntry]
    embeddings: Embeddings


class LinkingConfig(BaseRequest):
    scorer: LinkingScorer = LinkingScorer.SILHOUETTE
    metric: DistancesMetric = DistancesMetric.EUCLIDEAN
    embedding_source: EmbeddingSource = EmbeddingSource.OPENAI
    method: ClusteringMethod


class LinkingRequest(BaseRequest):
    entries: list[Entry]
    config: LinkingConfig
    settings: dict
    return_plot_data: bool = False


class LinkingResponse(BaseModel):
    results: list[ClusteringEntry]
    embeddings: Embeddings | None = None


# Summarizer API


class EditorConfig(BaseModel):
    style: str
    model: OpenAIModels


class SummaryConfig(BaseModel):
    summary_model: OpenAIModels
    editor_config: EditorConfig | None = None


class SummaryRequest(BaseRequest):
    story: list[str]
    summary_method: SummaryMethod
    config: SummaryConfig
    density: Density


class CategorizeRequest(BaseRequest):
    story: list[str]
    config: SummaryConfig


# Supervisor API


class SummarizeRequest(ExternalRequest):
    config_id: int
    story_id: str
    preset_id: str
    required_density: list[Density]


class CategoryTitleRequest(ExternalRequest):
    config_id: int
    preset_id: str
    texts: list[str]


class FetchRequest(ExternalRequest):
    preset_id: str
    end_date: str
    offset_date: str | None = None
    social: bool = False
    config_id: int | None = None


class StoryEntry(BaseModel):
    uuid: UUID
    noise: bool = False


class CategoryEntry(BaseModel):
    uuid: UUID
    stories: list[StoryEntry]


class FetchResponse(BaseModel):
    config_id: int
    categories: list[CategoryEntry]
    skipped_channel_ids: list[int]


class CallbackPostRequest(BaseRequest):
    callback_data: dict


class ConfigPostRequest(BaseRequest):
    config_id: int
    embedding_source: EmbeddingSource
    linking_method: ClusteringMethod
    category_method: CategoryMethod
    summary_method: OpenAIModels
    editor_model: OpenAIModels


class CallbackPatchRequest(BaseRequest):
    callback_id: UUID
    callback_data: dict


class UserRequest(ExternalRequest):
    chat_id: int


class PartialPresetUpdate(ExternalRequest):
    preset_id: UUID
    preset_name: str | None = None
    chat_folder_link: str | None = None
    editor_prompt: str | None = None
    inactive: bool | None = None


class UserFeedbackRequest(BaseRequest):
    summary_id: UUID
    density: Density
    feedback: UserFeedbackValue | None = None
