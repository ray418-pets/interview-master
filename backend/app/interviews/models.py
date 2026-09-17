from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    direction = Column(String(32), nullable=False)
    segments = Column(JSON, nullable=False)
    status = Column(String(16), nullable=False, default="in_progress")
    started_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    records = relationship(
        "InterviewRecord", back_populates="session", order_by="InterviewRecord.round_index"
    )


class InterviewRecord(Base):
    __tablename__ = "interview_records"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), index=True, nullable=False)
    round_index = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(5000), nullable=True)
    feedback = Column(String(2000), nullable=True)

    session = relationship("InterviewSession", back_populates="records")
    question = relationship("Question")
