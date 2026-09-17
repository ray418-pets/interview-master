from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_db
from app.core.schemas import ApiResponse
from app.engine.rule_based import RuleBasedEngine
from app.interviews import service
from app.interviews.schemas import CreateSessionRequest, SubmitAnswerRequest
from app.users.deps import get_current_user
from app.users.models import User

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


def get_engine() -> RuleBasedEngine:
    return RuleBasedEngine()


@router.post("")
def create_session(
    payload: CreateSessionRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
    engine: RuleBasedEngine = Depends(get_engine),
):
    result = service.create_session(
        db,
        user.id,
        engine,
        template_id=payload.template_id,
        direction=payload.direction,
        segments=payload.segments,
    )
    return ApiResponse(data=result.model_dump())


@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    payload: SubmitAnswerRequest,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
    engine: RuleBasedEngine = Depends(get_engine),
):
    result = service.submit_answer(db, session_id, user.id, payload.answer, engine)
    return ApiResponse(data=result.model_dump())


@router.post("/{session_id}/finish")
def finish_session(
    session_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = service.finish_session(db, session_id, user.id)
    return ApiResponse(data=result.model_dump())


@router.get("")
def list_sessions(
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = service.list_sessions(db, user.id)
    return ApiResponse(data=[item.model_dump() for item in result])
