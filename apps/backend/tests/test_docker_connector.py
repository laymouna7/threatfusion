"""
Teste la logique de traduction du connecteur Docker (mapping de statut, calcul
CPU, gestion des erreurs) sans avoir besoin d'un vrai daemon Docker.
"""

import uuid
from unittest.mock import MagicMock, patch

from docker.errors import NotFound

from app.services.docker_connector import check_container_health, _compute_cpu_percent


def test_running_container_maps_to_healthy():
    resource_id = uuid.uuid4()
    fake_container = MagicMock()
    fake_container.status = "running"
    fake_container.short_id = "abc123"
    fake_container.attrs = {"RestartCount": 0}
    fake_container.stats.return_value = {
        "cpu_stats": {"cpu_usage": {"total_usage": 200}, "system_cpu_usage": 1000, "online_cpus": 2},
        "precpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 900},
    }

    fake_client = MagicMock()
    fake_client.containers.get.return_value = fake_container

    with patch("app.services.docker_connector.get_docker_client", return_value=fake_client):
        health = check_container_health(resource_id, "auth-service")

    assert health.status == "healthy"
    assert health.orchestrator == "docker"
    assert health.details["container_id"] == "abc123"


def test_container_not_found_maps_to_down():
    resource_id = uuid.uuid4()
    fake_client = MagicMock()
    fake_client.containers.get.side_effect = NotFound("no such container")

    with patch("app.services.docker_connector.get_docker_client", return_value=fake_client):
        health = check_container_health(resource_id, "ghost-service")

    assert health.status == "down"
    assert "error" in health.details


def test_compute_cpu_percent_handles_zero_delta():
    stats = {
        "cpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 500, "online_cpus": 1},
        "precpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 500},
    }
    assert _compute_cpu_percent(stats) == 0.0
