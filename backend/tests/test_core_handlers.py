from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppError
from app.core.handlers import register_exception_handlers


def build_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise AppError(code=40001, message="boom", status_code=400)

    @app.get("/unexpected")
    def unexpected():
        raise RuntimeError("secret detail")

    return app


def test_app_error_returns_unified_structure():
    client = TestClient(build_app())
    resp = client.get("/boom")
    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == 40001
    assert body["message"] == "boom"


def test_unhandled_error_returns_500_without_leaking_details():
    client = TestClient(build_app(), raise_server_exceptions=False)
    resp = client.get("/unexpected")
    assert resp.status_code == 500
    body = resp.json()
    assert body["code"] == 50000
    assert "secret detail" not in body["message"]
