from pydantic import BaseModel, ConfigDict

from app.questions.schemas import Segment


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    direction: str
    segments: list[Segment]


class CustomConfig(BaseModel):
    direction: str
    segments: list[Segment]
