def test_register_endpoint(client):
    resp = client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "secret123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"]["user"]["username"] == "alice"
    assert body["data"]["token"]


def test_login_endpoint(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "secret123"})
    assert resp.status_code == 200
    assert resp.json()["data"]["token"]


def test_login_wrong_password_returns_401(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["code"] == 40101


def test_register_duplicate_returns_409(client):
    client.post("/api/auth/register", json={"username": "alice", "password": "secret123"})
    resp = client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "secret123"},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == 40901
