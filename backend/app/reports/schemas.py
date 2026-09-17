from pydantic import BaseModel


class QuestionReview(BaseModel):
    question_content: str
    user_answer: str
    feedback: str


class ReportResponse(BaseModel):
    session_id: int
    direction: str
    status: str
    overall_evaluation: str
    improvement_suggestions: str
    questions: list[QuestionReview]
