from app.core.schemas import ApiResponse, ErrorResponse


def test_api_response_defaults():
    resp = ApiResponse()
    assert resp.code == 0
    assert resp.message == "success"
    assert resp.data is None


def test_api_response_with_data():
    resp = ApiResponse(data={"a": 1})
    assert resp.data == {"a": 1}


def test_error_response_fields():
    resp = ErrorResponse(code=40001, message="boom")
    assert resp.code == 40001
    assert resp.message == "boom"
