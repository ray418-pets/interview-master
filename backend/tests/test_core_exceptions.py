from app.core.exceptions import AppError


def test_app_error_carries_code_message_and_status_code():
    err = AppError(code=40001, message="boom", status_code=400)
    assert err.code == 40001
    assert err.message == "boom"
    assert err.status_code == 400


def test_app_error_default_status_code_is_400():
    err = AppError(code=1, message="x")
    assert err.status_code == 400


def test_app_error_is_an_exception():
    err = AppError(code=1, message="x")
    assert isinstance(err, Exception)
