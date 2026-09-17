def _register(client, username="alice"):
    client.post("/api/auth/register", json={"username": username, "password": "secret123"})
    resp = client.post("/api/auth/login", json={"username": username, "password": "secret123"})
    return resp.json()["data"]["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_interview_requires_auth(client):
    resp = client.post("/api/interviews", json={"template_id": 1})
    assert resp.status_code == 401


def test_create_interview_with_template(client):
    token = _register(client)
    resp = client.post("/api/interviews", json={"template_id": 1}, headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["session_id"]
    assert data["current_question"]["content"]


def test_create_interview_with_custom_config(client):
    token = _register(client)
    resp = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 2}]},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["total_questions"] == 2


def test_create_interview_invalid_config(client):
    token = _register(client)
    resp = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": []},
        headers=_auth(token),
    )
    assert resp.status_code == 400


def test_answer_and_finish_flow(client):
    token = _register(client)
    create = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 2}]},
        headers=_auth(token),
    ).json()["data"]
    sid = create["session_id"]

    answer = client.post(
        f"/api/interviews/{sid}/answer",
        json={"answer": "这是一个足够长的回答内容，包含关键词"},
        headers=_auth(token),
    )
    assert answer.status_code == 200
    assert answer.json()["data"]["is_finished"] is False

    finish = client.post(f"/api/interviews/{sid}/finish", headers=_auth(token))
    assert finish.status_code == 200
    assert finish.json()["data"]["status"] == "finished"


def test_answer_cross_user_forbidden(client):
    token_a = _register(client, "alice")
    token_b = _register(client, "bob")
    create = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 1}]},
        headers=_auth(token_a),
    ).json()["data"]
    resp = client.post(
        f"/api/interviews/{create['session_id']}/answer",
        json={"answer": "这是一个足够长的回答内容"},
        headers=_auth(token_b),
    )
    assert resp.status_code == 403


def test_list_interviews(client):
    token = _register(client)
    client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 1}]},
        headers=_auth(token),
    )
    resp = client.get("/api/interviews", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["status"] == "in_progress"
