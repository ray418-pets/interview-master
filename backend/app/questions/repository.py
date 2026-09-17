from sqlalchemy.orm import Session as DbSession

from app.questions.models import Question


def get_by_id(db: DbSession, question_id: int) -> Question | None:
    return db.query(Question).filter(Question.id == question_id).first()


def list_by_filter(
    db: DbSession,
    direction: str | None = None,
    question_types: list[str] | None = None,
    difficulty: str | None = None,
) -> list[Question]:
    query = db.query(Question)
    if direction is not None:
        query = query.filter(Question.direction == direction)
    if question_types:
        query = query.filter(Question.question_type.in_(question_types))
    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)
    return query.order_by(Question.id).all()


def count_by_filter(
    db: DbSession,
    direction: str | None = None,
    question_types: list[str] | None = None,
    difficulty: str | None = None,
) -> int:
    query = db.query(Question)
    if direction is not None:
        query = query.filter(Question.direction == direction)
    if question_types:
        query = query.filter(Question.question_type.in_(question_types))
    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)
    return query.count()


def bulk_insert(db: DbSession, questions: list[Question]) -> None:
    db.add_all(questions)
    db.commit()
