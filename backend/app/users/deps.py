from fastapi import Depends, Header
from sqlalchemy.orm import Session as DbSession

from app.core.deps import get_db
from app.core.exceptions import AppError
from app.users import repository
from app.users.models import User


def get_current_user(
    authorization: str = Header(None),
    db: DbSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError(code=40100, message="缺少认证信息", status_code=401)
    token = authorization[len("Bearer ") :].strip()
    if not token:
        raise AppError(code=40100, message="缺少认证信息", status_code=401)
    user = repository.get_user_by_token(db, token)
    if user is None:
        raise AppError(code=40101, message="登录已失效，请重新登录", status_code=401)
    return user
