from sqlalchemy.orm import Session as DbSession

from app.users.models import AuthSession, User


def get_user_by_username(db: DbSession, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_token(db: DbSession, token: str) -> User | None:
    auth_session = db.query(AuthSession).filter(AuthSession.token == token).first()
    if auth_session is None:
        return None
    return db.query(User).filter(User.id == auth_session.user_id).first()


def create_user(db: DbSession, username: str, password_hash: str) -> User:
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_session(db: DbSession, user_id: int, token: str) -> AuthSession:
    auth_session = AuthSession(user_id=user_id, token=token)
    db.add(auth_session)
    db.commit()
    db.refresh(auth_session)
    return auth_session
