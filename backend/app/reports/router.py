from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_db
from app.core.schemas import ApiResponse
from app.reports import service
from app.users.deps import get_current_user
from app.users.models import User

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{session_id}")
def get_report(
    session_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = service.get_report(db, session_id, user.id)
    return ApiResponse(data=result.model_dump())
