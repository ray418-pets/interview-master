from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AppError
from app.interviews import repository as interviews_repository
from app.reports import repository
from app.reports.models import Report
from app.reports.schemas import QuestionReview, ReportResponse

TYPE_LABELS = {
    "self_introduction": "自我介绍",
    "technical": "技术题",
    "behavioral": "行为题",
    "project_experience": "项目经验题",
    "open_ended": "开放题",
}


def _overall_evaluation(answered: int, total: int) -> str:
    if answered == total:
        return f"你已完整完成本次面试（{answered}/{total} 题），整体表现良好。"
    if answered >= total / 2:
        return f"你完成了本次面试的大部分题目（{answered}/{total} 题），整体表现中规中矩。"
    return f"本次面试仅完成 {answered}/{total} 题，建议后续多加练习。"


def _improvement_suggestions(unanswered_types: list[str]) -> str:
    if unanswered_types:
        labels = "、".join(TYPE_LABELS.get(t, t) for t in unanswered_types)
        return f"建议加强练习以下题型：{labels}；同时多复盘已答题目，巩固知识点。"
    return "建议多复盘本次面试的答题要点，并针对薄弱环节持续练习。"


def generate_report(db: DbSession, session_id: int) -> Report:
    records = interviews_repository.get_records(db, session_id)
    answered = [r for r in records if r.user_answer is not None]
    unanswered = [r for r in records if r.user_answer is None]

    unanswered_types = sorted({r.question.question_type for r in unanswered})
    report = Report(
        session_id=session_id,
        overall_evaluation=_overall_evaluation(len(answered), len(records)),
        improvement_suggestions=_improvement_suggestions(unanswered_types),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report(db: DbSession, session_id: int, user_id: int) -> ReportResponse:
    session = interviews_repository.get_session(db, session_id)
    if session is None:
        raise AppError(code=40401, message="会话不存在", status_code=404)
    if session.user_id != user_id:
        raise AppError(code=40301, message="无权访问该会话", status_code=403)
    if session.status == "in_progress":
        raise AppError(code=40903, message="面试尚未完成，暂无报告", status_code=409)

    report = repository.get_report(db, session_id)
    if report is None:
        report = generate_report(db, session_id)

    answered = interviews_repository.get_answered(db, session_id)
    questions = [
        QuestionReview(
            question_content=r.question.content,
            user_answer=r.user_answer,
            feedback=r.feedback,
        )
        for r in answered
    ]
    return ReportResponse(
        session_id=session.id,
        direction=session.direction,
        status=session.status,
        overall_evaluation=report.overall_evaluation,
        improvement_suggestions=report.improvement_suggestions,
        questions=questions,
    )
