import pytest

from app.core.exceptions import AppError
from app.users import repository, service
from app.users.schemas import LoginRequest, RegisterRequest


def test_register_creates_user_and_returns_token(db_session):
    result = service.register(
        db_session, RegisterRequest(username="alice", password="secret123")
    )
    assert result.token
    assert result.user.username == "alice"
    assert repository.get_user_by_username(db_session, "alice") is not None


def test_register_duplicate_username_raises_409(db_session):
    service.register(db_session, RegisterRequest(username="alice", password="secret123"))
    with pytest.raises(AppError) as exc_info:
        service.register(db_session, RegisterRequest(username="alice", password="other456"))
    assert exc_info.value.status_code == 409


def test_login_success_returns_token(db_session):
    service.register(db_session, RegisterRequest(username="alice", password="secret123"))
    result = service.login(db_session, LoginRequest(username="alice", password="secret123"))
    assert result.token
    assert result.user.username == "alice"


def test_login_wrong_password_raises_401(db_session):
    service.register(db_session, RegisterRequest(username="alice", password="secret123"))
    with pytest.raises(AppError) as exc_info:
        service.login(db_session, LoginRequest(username="alice", password="wrongpass"))
    assert exc_info.value.status_code == 401


def test_login_unknown_user_raises_401(db_session):
    with pytest.raises(AppError):
        service.login(db_session, LoginRequest(username="nobody", password="secret123"))
