from pydantic import BaseModel


# class PresetData(BaseModel):
#     preset_name: str
#     chat_folder_link: str
#     editor_prompt: str

#     @classmethod
#     def get_fields(cls):
#         return list(cls.model_fields.keys())

# class Config(BaseModel):
#     embedding_source: EmbeddingSource
#     linking_method: ClusteringMethod
#     category_method: CategoryMethod
#     summary_method: SummaryMethod
