from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_db
from app.core.schemas import ApiResponse
from app.users import service
from app.users.schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: DbSession = Depends(get_db)):
    result = service.register(db, payload)
    return ApiResponse(data=result.model_dump())


@router.post("/login")
def login(payload: LoginRequest, db: DbSession = Depends(get_db)):
    result = service.login(db, payload)
    return ApiResponse(data=result.model_dump())
