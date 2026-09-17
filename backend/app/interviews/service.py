from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AppError
from app.interviews import repository
from app.interviews.models import utcnow
from app.interviews.schemas import (
    CreateSessionResponse,
    CurrentQuestion,
    FinishSessionResponse,
    SessionListItem,
    SubmitAnswerResponse,
)
from app.templates import service as templates_service

MIN_ANSWER_LENGTH = 10


def create_session(
    db: DbSession,
    user_id: int,
    engine,
    template_id: int | None = None,
    direction: str | None = None,
    segments: list | None = None,
) -> CreateSessionResponse:
    if segments is not None:
        segments = [s if isinstance(s, dict) else s.model_dump() for s in segments]
    custom = None if (direction is None and segments is None) else (direction, segments)
    direction, segments = templates_service.resolve_config(
        db, template_id=template_id, custom_config=custom
    )
    questions = engine.draw_questions(db, direction, segments)
    session = repository.create_session(db, user_id, direction, segments, questions)
    return CreateSessionResponse(
        session_id=session.id,
        direction=direction,
        total_questions=len(questions),
        status=session.status,
        current_question=CurrentQuestion(round_index=0, content=questions[0].content),
    )


def submit_answer(
    db: DbSession, session_id: int, user_id: int, answer: str, engine
) -> SubmitAnswerResponse:
    session = repository.get_session(db, session_id)
    if session is None:
        raise AppError(code=40401, message="会话不存在", status_code=404)
    if session.user_id != user_id:
        raise AppError(code=40301, message="无权访问该会话", status_code=403)
    if session.status != "in_progress":
        raise AppError(code=40902, message="会话已结束，无法继续作答", status_code=409)

    records = repository.get_records(db, session_id)
    current = next((r for r in records if r.user_answer is None), None)
    if current is None:
        raise AppError(code=40902, message="会话已结束，无法继续作答", status_code=409)

    stripped = answer.strip() if answer else ""
    if len(stripped) < MIN_ANSWER_LENGTH:
        return SubmitAnswerResponse(
            feedback=f"回答过短，请至少输入 {MIN_ANSWER_LENGTH} 个字符后再提交。",
            is_finished=False,
            next_question=CurrentQuestion(
                round_index=current.round_index, content=current.question.content
            ),
        )

    feedback = engine.evaluate_answer(current.question, stripped)
    current.user_answer = stripped
    current.feedback = feedback

    next_index = current.round_index + 1
    if next_index >= len(records):
        session.status = "completed"
        session.ended_at = utcnow()
        db.commit()
        return SubmitAnswerResponse(feedback=feedback, is_finished=True, next_question=None)

    next_record = records[next_index]
    db.commit()
    return SubmitAnswerResponse(
        feedback=feedback,
        is_finished=False,
        next_question=CurrentQuestion(
            round_index=next_record.round_index, content=next_record.question.content
        ),
    )


def finish_session(
    db: DbSession, session_id: int, user_id: int
) -> FinishSessionResponse:
    session = repository.get_session(db, session_id)
    if session is None:
        raise AppError(code=40401, message="会话不存在", status_code=404)
    if session.user_id != user_id:
        raise AppError(code=40301, message="无权访问该会话", status_code=403)
    if session.status != "in_progress":
        raise AppError(code=40902, message="会话已结束，无法操作", status_code=409)

    session.status = "finished"
    session.ended_at = utcnow()
    db.commit()
    return FinishSessionResponse(session_id=session.id, status=session.status)


def list_sessions(db: DbSession, user_id: int) -> list[SessionListItem]:
    sessions = repository.list_by_user(db, user_id)
    return [
        SessionListItem(
            id=s.id,
            direction=s.direction,
            total_questions=len(s.records),
            started_at=s.started_at,
            status=s.status,
        )
        for s in sessions
    ]
