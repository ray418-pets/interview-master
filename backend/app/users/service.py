import secrets

import bcrypt
from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AppError
from app.users import repository
from app.users.schemas import AuthResponse, LoginRequest, RegisterRequest, UserOut


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _issue_token() -> str:
    return secrets.token_urlsafe(32)


def register(db: DbSession, payload: RegisterRequest) -> AuthResponse:
    if repository.get_user_by_username(db, payload.username) is not None:
        raise AppError(code=40901, message="用户名已被占用", status_code=409)
    user = repository.create_user(
        db, payload.username, _hash_password(payload.password)
    )
    token = _issue_token()
    repository.create_session(db, user.id, token)
    return AuthResponse(token=token, user=UserOut.model_validate(user))


def login(db: DbSession, payload: LoginRequest) -> AuthResponse:
    user = repository.get_user_by_username(db, payload.username)
    if user is None or not _verify_password(payload.password, user.password_hash):
        raise AppError(code=40101, message="用户名或密码错误", status_code=401)
    token = _issue_token()
    repository.create_session(db, user.id, token)
    return AuthResponse(token=token, user=UserOut.model_validate(user))
