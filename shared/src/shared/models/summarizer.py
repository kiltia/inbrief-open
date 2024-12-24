from pydantic import BaseModel


# class EditorConfig(BaseModel):
#     style: str
#     model: OpenAIModels


# class SummaryConfig(BaseModel):
#     summary_model: OpenAIModels
#     editor_config: EditorConfig | None = None


# class SummaryRequest(BaseRequest):
#     story: list[str]
#     summary_method: SummaryMethod
#     config: SummaryConfig
#     density: Density


# class CategorizeRequest(BaseRequest):
#     story: list[str]
#     config: SummaryConfig
