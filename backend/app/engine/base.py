from typing import Protocol

from app.questions.models import Question


class InterviewEngine(Protocol):
    def draw_questions(
        self,
        db,
        direction: str,
        segments: list[dict],
        difficulty: str | None = None,
    ) -> list[Question]: ...

    def evaluate_answer(self, question: Question, answer: str) -> str: ...
