import json
from pathlib import Path

from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AppError
from app.questions import repository
from app.questions.enums import Difficulty, Direction, QuestionType
from app.questions.models import Question


def filter_questions(
    db: DbSession,
    direction: str,
    question_types: list[str],
    difficulty: str | None = None,
) -> list[Question]:
    if direction not in {item.value for item in Direction}:
        raise AppError(code=40001, message="无效的岗位方向")
    for question_type in question_types:
        if question_type not in {item.value for item in QuestionType}:
            raise AppError(code=40002, message="无效的题型")
    if difficulty is not None and difficulty not in {item.value for item in Difficulty}:
        raise AppError(code=40003, message="无效的难度")
    return repository.list_by_filter(
        db, direction=direction, question_types=question_types, difficulty=difficulty
    )


def _load_seed_questions() -> list[dict]:
    seed_path = Path(__file__).with_name("seed_data.json")
    with seed_path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_if_empty(db: DbSession) -> None:
    if repository.count_by_filter(db) > 0:
        return
    questions = [
        Question(
            direction=item["direction"],
            question_type=item["question_type"],
            difficulty=item["difficulty"],
            content=item["content"],
            reference_points=item["reference_points"],
        )
        for item in _load_seed_questions()
    ]
    repository.bulk_insert(db, questions)
