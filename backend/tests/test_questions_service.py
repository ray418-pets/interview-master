import pytest

from app.core.exceptions import AppError
from app.questions import repository, service
from app.questions.enums import Direction, QuestionType


def test_seed_if_empty_imports_questions(db_session):
    service.seed_if_empty(db_session)
    assert repository.count_by_filter(db_session) >= 100


def test_seed_if_empty_is_idempotent(db_session):
    service.seed_if_empty(db_session)
    first = repository.count_by_filter(db_session)
    service.seed_if_empty(db_session)
    assert repository.count_by_filter(db_session) == first


def test_seed_covers_all_directions_and_types(db_session):
    service.seed_if_empty(db_session)
    for direction in Direction:
        for question_type in QuestionType:
            questions = repository.list_by_filter(
                db_session, direction=direction.value, question_types=[question_type.value]
            )
            assert len(questions) >= 1


def test_filter_questions_by_direction_and_type(db_session):
    service.seed_if_empty(db_session)
    questions = service.filter_questions(db_session, "technical_backend", ["technical"])
    assert questions
    assert all(q.direction == "technical_backend" for q in questions)
    assert all(q.question_type == "technical" for q in questions)


def test_filter_questions_by_difficulty(db_session):
    service.seed_if_empty(db_session)
    questions = service.filter_questions(
        db_session, "general", ["behavioral"], difficulty="easy"
    )
    assert questions
    assert all(q.difficulty == "easy" for q in questions)


def test_filter_questions_rejects_invalid_direction(db_session):
    with pytest.raises(AppError):
        service.filter_questions(db_session, "not_a_direction", ["technical"])


def test_filter_questions_rejects_invalid_question_type(db_session):
    with pytest.raises(AppError):
        service.filter_questions(db_session, "general", ["not_a_type"])


def test_filter_questions_rejects_invalid_difficulty(db_session):
    with pytest.raises(AppError):
        service.filter_questions(
            db_session, "general", ["behavioral"], difficulty="impossible"
        )
