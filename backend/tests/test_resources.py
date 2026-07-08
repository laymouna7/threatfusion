def _create_sample_resource(client, name="auth-service"):
    return client.post(
        "/resources/",
        json={
            "name": name,
            "type": "api",
            "orchestrator": "docker",
            "config": {"image": "myapp/auth:1.0"},
        },
    )


def test_register_resource(client):
    response = _create_sample_resource(client)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "auth-service"
    assert body["orchestrator"] == "docker"
    assert body["config"]["image"] == "myapp/auth:1.0"


def test_register_duplicate_resource_rejected(client):
    _create_sample_resource(client)
    response = _create_sample_resource(client)
    assert response.status_code == 409


def test_list_resources(client):
    _create_sample_resource(client, name="service-a")
    _create_sample_resource(client, name="service-b")
    response = client.get("/resources/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_resource_not_found(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/resources/{fake_id}")
    assert response.status_code == 404


def test_delete_resource(client):
    created = _create_sample_resource(client).json()
    response = client.delete(f"/resources/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/resources/{created['id']}").status_code == 404


def test_register_resource_creates_audit_entry(client):
    created = _create_sample_resource(client).json()
    audit = client.get(f"/audit/{created['id']}").json()
    assert len(audit) == 1
    assert audit[0]["action"] == "resource_created"
