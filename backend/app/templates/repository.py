from sqlalchemy.orm import Session as DbSession

from app.templates.models import InterviewTemplate


def get_by_id(db: DbSession, template_id: int) -> InterviewTemplate | None:
    return db.query(InterviewTemplate).filter(InterviewTemplate.id == template_id).first()


def list_all(db: DbSession) -> list[InterviewTemplate]:
    return db.query(InterviewTemplate).order_by(InterviewTemplate.id).all()


def count(db: DbSession) -> int:
    return db.query(InterviewTemplate).count()


def bulk_insert(db: DbSession, templates: list[InterviewTemplate]) -> None:
    db.add_all(templates)
    db.commit()
