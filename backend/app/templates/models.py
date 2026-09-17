from sqlalchemy import JSON, Column, Integer, String

from app.core.database import Base


class InterviewTemplate(Base):
    __tablename__ = "interview_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    direction = Column(String(32), nullable=False)
    segments = Column(JSON, nullable=False)
