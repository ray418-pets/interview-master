from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer, ForeignKey("interview_sessions.id"), unique=True, nullable=False
    )
    overall_evaluation = Column(String(2000), nullable=False)
    improvement_suggestions = Column(String(2000), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("InterviewSession")
