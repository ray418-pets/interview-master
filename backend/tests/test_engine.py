import random

import pytest

from app.core.exceptions import AppError
from app.questions import service as questions_service
from app.questions.models import Question


def _make_question(reference_points):
    return Question(
        direction="general",
        question_type="behavioral",
        difficulty="easy",
        content="请谈谈你对该话题的看法。",
        reference_points=reference_points,
    )


def test_draw_questions_returns_correct_count_and_type(db_session):
    from app.engine.rule_based import RuleBasedEngine

    questions_service.seed_if_empty(db_session)
    engine = RuleBasedEngine()
    result = engine.draw_questions(
        db_session,
        "technical_backend",
        [{"type": "technical", "count": 3}],
    )
    assert len(result) == 3
    assert all(q.direction == "technical_backend" for q in result)
    assert all(q.question_type == "technical" for q in result)


def test_draw_questions_respects_segment_order_and_counts(db_session):
    from app.engine.rule_based import RuleBasedEngine

    questions_service.seed_if_empty(db_session)
    engine = RuleBasedEngine()
    result = engine.draw_questions(
        db_session,
        "general",
        [
            {"type": "self_introduction", "count": 1},
            {"type": "behavioral", "count": 2},
        ],
    )
    assert [q.question_type for q in result] == [
        "self_introduction",
        "behavioral",
        "behavioral",
    ]


def test_draw_questions_raises_when_not_enough_questions(db_session):
    from app.engine.rule_based import RuleBasedEngine

    questions_service.seed_if_empty(db_session)
    engine = RuleBasedEngine()
    with pytest.raises(AppError):
        engine.draw_questions(
            db_session,
            "technical_backend",
            [{"type": "technical", "count": 100}],
        )


def test_draw_questions_is_deterministic_with_seeded_rng(db_session):
    from app.engine.rule_based import RuleBasedEngine

    questions_service.seed_if_empty(db_session)
    first = RuleBasedEngine(rng=random.Random(42)).draw_questions(
        db_session,
        "technical_backend",
        [{"type": "technical", "count": 3}],
    )
    second = RuleBasedEngine(rng=random.Random(42)).draw_questions(
        db_session,
        "technical_backend",
        [{"type": "technical", "count": 3}],
    )
    assert [q.id for q in first] == [q.id for q in second]


def test_evaluate_answer_positive_when_all_points_hit():
    from app.engine.rule_based import RuleBasedEngine

    engine = RuleBasedEngine()
    question = _make_question(["索引", "事务"])
    feedback = engine.evaluate_answer(question, "我在项目中用到了索引和事务来保证性能与一致性")
    assert "覆盖了全部参考要点" in feedback


def test_evaluate_answer_partial_lists_missed_points():
    from app.engine.rule_based import RuleBasedEngine

    engine = RuleBasedEngine()
    question = _make_question(["索引", "事务"])
    feedback = engine.evaluate_answer(question, "我主要讲了索引优化")
    assert "覆盖了部分要点" in feedback
    assert "事务" in feedback


def test_evaluate_answer_hint_when_nothing_hits():
    from app.engine.rule_based import RuleBasedEngine

    engine = RuleBasedEngine()
    question = _make_question(["索引", "事务"])
    feedback = engine.evaluate_answer(question, "随便说说")
    assert "未命中参考要点" in feedback
    assert "索引" in feedback
    assert "事务" in feedback


def test_evaluate_answer_without_reference_points():
    from app.engine.rule_based import RuleBasedEngine

    engine = RuleBasedEngine()
    question = _make_question([])
    feedback = engine.evaluate_answer(question, "任意回答")
    assert feedback
