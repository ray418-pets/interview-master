from sqlalchemy.orm import Session as DbSession

from app.reports.models import Report


def get_report(db: DbSession, session_id: int) -> Report | None:
    return db.query(Report).filter(Report.session_id == session_id).first()
