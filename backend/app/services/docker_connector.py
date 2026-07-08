"""
Connecteur Docker : interroge l'API Docker et traduit le statut d'un conteneur
vers le schéma pivot défini dans ADR 0003 / app.schemas.health.

Toute la logique spécifique à Docker est isolée ici — le reste de l'app ne
manipule jamais un objet `docker.models.containers.Container` directement.
"""

from datetime import datetime, timezone

import docker
from docker.errors import DockerException, NotFound

from app.schemas.health import ResourceHealth

# Mapping du statut natif Docker vers notre statut unifié
_DOCKER_STATUS_MAP = {
    "running": "healthy",
    "restarting": "degraded",
    "paused": "degraded",
    "exited": "down",
    "dead": "down",
    "created": "unknown",
}


def get_docker_client() -> docker.DockerClient:
    """
    Instancie le client Docker à partir de l'environnement (socket monté dans
    le conteneur backend, ex: /var/run/docker.sock).
    """
    return docker.from_env()


def check_container_health(resource_id, container_name: str) -> ResourceHealth:
    """
    Interroge un conteneur par son nom et retourne son état dans le format pivot.

    Si le conteneur n'existe pas ou si Docker est injoignable, retourne un
    statut 'unknown' plutôt que de laisser planter l'appelant (le monitoring
    ne doit jamais crasher juste parce qu'une ressource a disparu).
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_name)
        container.reload()  # rafraîchit les stats avant lecture

        stats = container.stats(stream=False)
        cpu_percent = _compute_cpu_percent(stats)

        return ResourceHealth(
            resource_id=resource_id,
            status=_DOCKER_STATUS_MAP.get(container.status, "unknown"),
            orchestrator="docker",
            last_checked=datetime.now(timezone.utc),
            details={
                "container_id": container.short_id,
                "state": container.status,
                "cpu_percent": round(cpu_percent, 2),
                "restart_count": container.attrs.get("RestartCount", 0),
            },
        )
    except NotFound:
        return ResourceHealth(
            resource_id=resource_id,
            status="down",
            orchestrator="docker",
            last_checked=datetime.now(timezone.utc),
            details={"error": "container introuvable"},
        )
    except DockerException as e:
        return ResourceHealth(
            resource_id=resource_id,
            status="unknown",
            orchestrator="docker",
            last_checked=datetime.now(timezone.utc),
            details={"error": str(e)},
        )


def _compute_cpu_percent(stats: dict) -> float:
    """Calcule le % CPU à partir des deltas de stats Docker (formule standard Docker CLI)."""
    try:
        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        )
        num_cpus = stats["cpu_stats"].get("online_cpus", 1)
        if system_delta > 0 and cpu_delta > 0:
            return (cpu_delta / system_delta) * num_cpus * 100.0
    except (KeyError, ZeroDivisionError):
        pass
    return 0.0


def deploy_container(image: str, name: str, env: dict | None = None) -> str:
    """
    Lance un conteneur à partir d'une image. Retourne l'ID du conteneur créé.
    Utilisé par la tâche Celery de déploiement (services/deployment.py).
    """
    client = get_docker_client()
    container = client.containers.run(
        image=image,
        name=name,
        environment=env or {},
        detach=True,
        restart_policy={"Name": "unless-stopped"},
    )
    return container.id
