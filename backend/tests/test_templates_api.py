def test_list_templates_endpoint(client):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    templates = body["data"]
    assert isinstance(templates, list)
    assert templates
    first = templates[0]
    assert "id" in first
    assert "name" in first
    assert "direction" in first
    assert "segments" in first
