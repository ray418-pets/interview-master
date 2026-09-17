from sqlalchemy.orm import Session as DbSession

from app.interviews.models import InterviewRecord, InterviewSession
from app.questions.models import Question


def create_session(
    db: DbSession,
    user_id: int,
    direction: str,
    segments: list[dict],
    questions: list[Question],
) -> InterviewSession:
    session = InterviewSession(
        user_id=user_id, direction=direction, segments=segments, status="in_progress"
    )
    db.add(session)
    db.flush()
    for index, question in enumerate(questions):
        db.add(
            InterviewRecord(
                session_id=session.id, round_index=index, question_id=question.id
            )
        )
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DbSession, session_id: int) -> InterviewSession | None:
    return db.query(InterviewSession).filter(InterviewSession.id == session_id).first()


def list_by_user(db: DbSession, user_id: int) -> list[InterviewSession]:
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )


def get_records(db: DbSession, session_id: int) -> list[InterviewRecord]:
    return (
        db.query(InterviewRecord)
        .filter(InterviewRecord.session_id == session_id)
        .order_by(InterviewRecord.round_index)
        .all()
    )


def get_answered(db: DbSession, session_id: int) -> list[InterviewRecord]:
    return (
        db.query(InterviewRecord)
        .filter(
            InterviewRecord.session_id == session_id,
            InterviewRecord.user_answer.isnot(None),
        )
        .order_by(InterviewRecord.round_index)
        .all()
    )
