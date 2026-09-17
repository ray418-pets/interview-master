import random

from app.core.exceptions import AppError
from app.questions import service as questions_service
from app.questions.models import Question


class RuleBasedEngine:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()

    def draw_questions(
        self,
        db,
        direction: str,
        segments: list[dict],
        difficulty: str | None = None,
    ) -> list[Question]:
        result: list[Question] = []
        for segment in segments:
            candidates = questions_service.filter_questions(
                db, direction, [segment["type"]], difficulty
            )
            if len(candidates) < segment["count"]:
                raise AppError(code=40004, message="题目数量不足")
            result.extend(self.rng.sample(candidates, segment["count"]))
        return result

    def evaluate_answer(self, question: Question, answer: str) -> str:
        points = [p for p in (question.reference_points or []) if p]
        if not points:
            return "回答已记录。"
        hit = [p for p in points if p in answer]
        missed = [p for p in points if p not in answer]
        if not missed:
            return f"回答覆盖了全部参考要点（{'、'.join(points)}），回答较完整。"
        if hit:
            return f"回答覆盖了部分要点（{'、'.join(hit)}），建议补充：{'、'.join(missed)}。"
        return f"回答未命中参考要点，建议围绕以下要点展开：{'、'.join(points)}。"
