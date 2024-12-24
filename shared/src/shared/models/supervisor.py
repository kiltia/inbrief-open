# class SummarizeRequest(ExternalRequest):
#     config_id: int
#     story_id: str
#     preset_id: str
#     required_density: list[Density]


# class CategoryTitleRequest(ExternalRequest):
#     config_id: int
#     preset_id: str
#     texts: list[str]


# class FetchRequest(ExternalRequest):
#     preset_id: str
#     end_date: str
#     offset_date: str | None = None
#     social: bool = False
#     config_id: int | None = None


# class StoryEntry(BaseModel):
#     uuid: UUID
#     noise: bool = False


# class CategoryEntry(BaseModel):
#     uuid: UUID
#     stories: list[StoryEntry]


# class FetchResponse(BaseModel):
#     config_id: int
#     categories: list[CategoryEntry]
#     skipped_channel_ids: list[int]


# class CallbackPostRequest(BaseRequest):
#     callback_data: dict


# class ConfigPostRequest(BaseRequest):
#     config_id: int
#     embedding_source: EmbeddingSource
#     linking_method: ClusteringMethod
#     category_method: CategoryMethod
#     summary_method: OpenAIModels
#     editor_model: OpenAIModels


# class CallbackPatchRequest(BaseRequest):
#     callback_id: UUID
#     callback_data: dict


# class UserRequest(ExternalRequest):
#     chat_id: int


# class PartialPresetUpdate(ExternalRequest):
#     preset_id: UUID
#     preset_name: str | None = None
#     chat_folder_link: str | None = None
#     editor_prompt: str | None = None
#     inactive: bool | None = None


# class UserFeedbackRequest(BaseRequest):
#     summary_id: UUID
#     density: Density
#     feedback: UserFeedbackValue | None = None

# class UserFeedbackValue(str, Enum):
#     LIKE = "like"
#     BAD_LINKAGE = "bad_linkage"
#     BAD_CATEGORIZING = "bad_categorizing"
#     LEXICAL_OR_GRAMMAR_ERRORS = "errors"
#     FAKE_NEWS = "fake_news"
#     SUMMARY_TOO_SHORT = "too_short"
#     SUMMARY_TOO_LONG = "too_long"

# class OpenAIModels(str, Enum):
#     GPT3_TURBO = "gpt-3.5-turbo-1106"
#     GPT4 = "gpt-4"
#     GPT4_32k = "gpt-4-32k"
#     GPT4_TURBO = "gpt-4-1106-preview"

#     @classmethod
#     def has_value(cls, value):
#         return value in cls._value2member_map_
