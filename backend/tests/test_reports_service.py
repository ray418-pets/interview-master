import pytest

from app.core.exceptions import AppError
from app.engine.rule_based import RuleBasedEngine
from app.interviews import service as interviews_service
from app.reports import repository as reports_repository
from app.reports import service as reports_service
from app.reports.models import Report


@pytest.fixture()
def engine():
    return RuleBasedEngine()


def _completed_session(db, engine, user_id=1):
    result = interviews_service.create_session(
        db, user_id, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    sid = result.session_id
    interviews_service.submit_answer(db, sid, user_id, "这是一个足够长的回答内容，包含关键词", engine)
    interviews_service.submit_answer(db, sid, user_id, "这是第二个足够长的回答内容", engine)
    return sid


def test_get_report_for_completed_session(db_session, engine):
    sid = _completed_session(db_session, engine)
    report = reports_service.get_report(db_session, sid, 1)
    assert report.overall_evaluation
    assert report.improvement_suggestions
    assert len(report.questions) == 2
    assert report.questions[0].question_content
    assert report.questions[0].user_answer
    assert report.questions[0].feedback


def test_get_report_is_idempotent(db_session, engine):
    sid = _completed_session(db_session, engine)
    reports_service.get_report(db_session, sid, 1)
    reports_service.get_report(db_session, sid, 1)
    count = db_session.query(Report).filter(Report.session_id == sid).count()
    assert count == 1


def test_get_report_for_finished_session_only_answered(db_session, engine):
    result = interviews_service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    interviews_service.submit_answer(
        db_session, result.session_id, 1, "这是一个足够长的回答内容", engine
    )
    interviews_service.finish_session(db_session, result.session_id, 1)
    report = reports_service.get_report(db_session, result.session_id, 1)
    assert len(report.questions) == 1


def test_get_report_in_progress_raises(db_session, engine):
    result = interviews_service.create_session(
        db_session, 1, engine, direction="general",
        segments=[{"type": "behavioral", "count": 2}],
    )
    with pytest.raises(AppError) as exc_info:
        reports_service.get_report(db_session, result.session_id, 1)
    assert exc_info.value.status_code == 409


def test_get_report_missing_session_raises(db_session, engine):
    with pytest.raises(AppError) as exc_info:
        reports_service.get_report(db_session, 99999, 1)
    assert exc_info.value.status_code == 404


def test_get_report_cross_user_forbidden(db_session, engine):
    sid = _completed_session(db_session, engine, user_id=1)
    with pytest.raises(AppError) as exc_info:
        reports_service.get_report(db_session, sid, 2)
    assert exc_info.value.status_code == 403


def test_generate_report_creates_row(db_session, engine):
    sid = _completed_session(db_session, engine)
    report = reports_service.generate_report(db_session, sid)
    assert reports_repository.get_report(db_session, sid) is not None
    assert report.session_id == sid
