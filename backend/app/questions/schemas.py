from pydantic import BaseModel, ConfigDict


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direction: str
    question_type: str
    difficulty: str
    content: str
    reference_points: list[str]


class Segment(BaseModel):
    type: str
    count: int
