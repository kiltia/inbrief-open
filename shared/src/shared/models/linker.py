from enum import Enum
from pydantic import BaseModel

# class LinkingScorer(str, Enum):
#     SILHOUETTE = "silhouette"
#     CALINSKI_HARABASZ = "calinski_harabasz"
#     WEIGHTED_SCORER = "weighted_scorer"
#     BUSINESS_SCORER = "business_scorer"


# class DistancesMetric(str, Enum):
#     CITYBLOCK = "cityblock"
#     COSINE = "cosine"
#     EUCLIDEAN = "euclidean"


# class Entry(BaseModel):
#     text: str
#     embeddings: dict[str, list[float]]


# StoriesNums = list[list[int]]
# Embeddings = list[list[float]]


# class ClusteringMetadata(BaseModel):
#     score: float
#     config: dict


# class ClusteringEntry(BaseModel):
#     metadata: ClusteringMetadata | None = None
#     stories_nums: StoriesNums


# class PlotData(BaseModel):
#     payload: list[StorySources]
#     results: list[ClusteringEntry]
#     embeddings: Embeddings


# class LinkingConfig(BaseRequest):
#     scorer: LinkingScorer = LinkingScorer.SILHOUETTE
#     metric: DistancesMetric = DistancesMetric.EUCLIDEAN
#     embedding_source: EmbeddingSource = EmbeddingSource.JINA
#     method: ClusteringMethod


# class LinkingRequest(BaseRequest):
#     entries: list[Entry]
#     config: LinkingConfig
#     settings: dict
#     return_plot_data: bool = False


# class LinkingResponse(BaseModel):
#     results: list[ClusteringEntry]
#     embeddings: Embeddings | None = None

# def extend_enum(inherited_enum):
#     def wrapper(added_enum):
#         joined = {}
#         for item in inherited_enum:
#             joined[item.name] = item.value
#         for item in added_enum:
#             joined[item.name] = item.value
#         return Enum(added_enum.__name__, joined)

#     return wrapper
