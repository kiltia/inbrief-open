from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime


class Entity(BaseModel):
    created_at: Annotated[Optional[datetime], Field(default_factory=datetime.now)] = (
        None
    )
