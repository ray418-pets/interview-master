import pytest

from app.core.exceptions import AppError
from app.engine.rule_based import RuleBasedEngine
from app.interviews import repository, service


@pytest.fixture()
def engine():
    return RuleBasedEngine()


def test_create_session_returns_first_question(db_session, engine):
    result = service.create_session(db_session, 1, engine, template_id=1)
    assert result.session_id
    assert result.total_questions > 0
    assert result.status == "in_progress"
    assert result.current_question.round_index == 0
    assert result.current_question.content


def test_create_session_with_custom_config(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    assert result.total_questions == 2


def test_create_session_without_config_raises(db_session, engine):
    with pytest.raises(AppError):
        service.create_session(db_session, 1, engine)


def test_submit_answer_returns_feedback_and_next(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    resp = service.submit_answer(
        db_session, result.session_id, 1, "这是一个足够长的回答内容，包含关键词", engine
    )
    assert resp.feedback
    assert resp.is_finished is False
    assert resp.next_question is not None
    assert resp.next_question.round_index == 1


def test_submit_last_answer_completes_session(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 1}],
    )
    resp = service.submit_answer(
        db_session, result.session_id, 1, "这是一个足够长的回答内容，包含关键词", engine
    )
    assert resp.is_finished is True
    assert resp.next_question is None
    assert repository.get_session(db_session, result.session_id).status == "completed"


def test_submit_short_answer_is_blocked(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    resp = service.submit_answer(db_session, result.session_id, 1, "太短", engine)
    assert resp.is_finished is False
    assert "过短" in resp.feedback
    assert resp.next_question.round_index == 0
    assert len(repository.get_answered(db_session, result.session_id)) == 0


def test_submit_answer_cross_user_forbidden(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 1}],
    )
    with pytest.raises(AppError) as exc_info:
        service.submit_answer(
            db_session, result.session_id, 2, "这是一个足够长的回答内容", engine
        )
    assert exc_info.value.status_code == 403


def test_submit_answer_missing_session_raises(db_session, engine):
    with pytest.raises(AppError) as exc_info:
        service.submit_answer(db_session, 99999, 1, "这是一个足够长的回答内容", engine)
    assert exc_info.value.status_code == 404


def test_submit_answer_on_terminal_session_raises(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 1}],
    )
    service.submit_answer(db_session, result.session_id, 1, "这是一个足够长的回答内容", engine)
    with pytest.raises(AppError) as exc_info:
        service.submit_answer(db_session, result.session_id, 1, "再次提交一个回答内容", engine)
    assert exc_info.value.status_code == 409


def test_finish_session_sets_status(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    resp = service.finish_session(db_session, result.session_id, 1)
    assert resp.status == "finished"
    assert repository.get_session(db_session, result.session_id).status == "finished"


def test_finish_session_cross_user_forbidden(db_session, engine):
    result = service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    with pytest.raises(AppError) as exc_info:
        service.finish_session(db_session, result.session_id, 2)
    assert exc_info.value.status_code == 403


def test_list_sessions_only_returns_own(db_session, engine):
    service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 1}],
    )
    service.create_session(
        db_session, 2, engine, direction="general",
        segments=[{"type": "behavioral", "count": 1}],
    )
    result = service.list_sessions(db_session, 1)
    assert len(result) == 1
    assert result[0].direction == "general"
    assert result[0].total_questions == 1
