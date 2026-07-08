"""
On mock `run_deployment.delay` : ces tests vérifient le comportement de l'API
(création de l'entrée, statut 202, audit), pas l'exécution réelle de la tâche
Celery (qui nécessite RabbitMQ + Docker, testés séparément en intégration).
"""

from unittest.mock import MagicMock


def _create_sample_resource(client):
    return client.post(
        "/resources/",
        json={
            "name": "worker-service",
            "type": "worker",
            "orchestrator": "docker",
            "config": {"image": "myapp/worker:1.0"},
        },
    ).json()


def test_trigger_deployment(client, mocker):
    resource = _create_sample_resource(client)

    fake_task = MagicMock(id="fake-task-id")
    mocker.patch("app.api.deployments.run_deployment.delay", return_value=fake_task)

    response = client.post(f"/deployments/{resource['id']}")
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert body["resource_id"] == resource["id"]


def test_trigger_deployment_resource_not_found(client, mocker):
    mocker.patch("app.api.deployments.run_deployment.delay", return_value=MagicMock(id="x"))
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(f"/deployments/{fake_id}")
    assert response.status_code == 404


def test_trigger_deployment_creates_audit_entry(client, mocker):
    resource = _create_sample_resource(client)
    mocker.patch("app.api.deployments.run_deployment.delay", return_value=MagicMock(id="x"))

    client.post(f"/deployments/{resource['id']}")
    audit = client.get(f"/audit/{resource['id']}").json()
    actions = [a["action"] for a in audit]
    assert "deployment_triggered" in actions


def test_list_deployments(client, mocker):
    resource = _create_sample_resource(client)
    mocker.patch("app.api.deployments.run_deployment.delay", return_value=MagicMock(id="x"))

    client.post(f"/deployments/{resource['id']}")
    response = client.get(f"/deployments/{resource['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"
