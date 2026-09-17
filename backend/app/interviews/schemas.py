from datetime import datetime

from pydantic import BaseModel

from app.questions.schemas import Segment


class CreateSessionRequest(BaseModel):
    template_id: int | None = None
    direction: str | None = None
    segments: list[Segment] | None = None


class SubmitAnswerRequest(BaseModel):
    answer: str


class CurrentQuestion(BaseModel):
    round_index: int
    content: str


class CreateSessionResponse(BaseModel):
    session_id: int
    direction: str
    total_questions: int
    status: str
    current_question: CurrentQuestion


class SubmitAnswerResponse(BaseModel):
    feedback: str
    is_finished: bool
    next_question: CurrentQuestion | None


class FinishSessionResponse(BaseModel):
    session_id: int
    status: str


class SessionListItem(BaseModel):
    id: int
    direction: str
    total_questions: int
    started_at: datetime
    status: str
