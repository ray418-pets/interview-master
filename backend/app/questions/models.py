from sqlalchemy import JSON, Column, Integer, String

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    direction = Column(String(32), index=True, nullable=False)
    question_type = Column(String(32), index=True, nullable=False)
    difficulty = Column(String(16), index=True, nullable=False)
    content = Column(String(1000), nullable=False)
    reference_points = Column(JSON, nullable=False, default=list)
