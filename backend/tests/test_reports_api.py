def _register(client, username="alice"):
    client.post("/api/auth/register", json={"username": username, "password": "secret123"})
    resp = client.post("/api/auth/login", json={"username": username, "password": "secret123"})
    return resp.json()["data"]["token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _complete_session(client, token):
    create = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 1}]},
        headers=_auth(token),
    ).json()["data"]
    sid = create["session_id"]
    client.post(
        f"/api/interviews/{sid}/answer",
        json={"answer": "这是一个足够长的回答内容"},
        headers=_auth(token),
    )
    return sid


def test_get_report_requires_auth(client):
    resp = client.get("/api/reports/1")
    assert resp.status_code == 401


def test_get_report_completed(client):
    token = _register(client)
    sid = _complete_session(client, token)
    resp = client.get(f"/api/reports/{sid}", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["overall_evaluation"]
    assert data["improvement_suggestions"]
    assert len(data["questions"]) == 1


def test_get_report_in_progress(client):
    token = _register(client)
    create = client.post(
        "/api/interviews",
        json={"direction": "general", "segments": [{"type": "behavioral", "count": 1}]},
        headers=_auth(token),
    ).json()["data"]
    resp = client.get(f"/api/reports/{create['session_id']}", headers=_auth(token))
    assert resp.status_code == 409


def test_get_report_cross_user(client):
    token_a = _register(client, "alice")
    token_b = _register(client, "bob")
    sid = _complete_session(client, token_a)
    resp = client.get(f"/api/reports/{sid}", headers=_auth(token_b))
    assert resp.status_code == 403
