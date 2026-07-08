"""
Service d'agrégation de santé : c'est ici que le choix d'orchestrateur d'une
ressource (champ Resource.orchestrator) détermine quel connecteur appeler.
C'est la tâche planifiée par Celery beat (voir workers/celery_app.py).
"""

from app.db.session import SessionLocal
from app.models.resource import Resource
from app.services import docker_connector, k8s_connector
from app.workers.celery_app import celery_app


def _check_single_resource(resource: Resource):
    """Route vers le bon connecteur selon l'orchestrateur de la ressource."""
    if resource.orchestrator == "docker":
        container_name = resource.config.get("container_name", resource.name)
        return docker_connector.check_container_health(resource.id, container_name)

    if resource.orchestrator == "kubernetes":
        pod_name = resource.config.get("pod_name", resource.name)
        namespace = resource.config.get("namespace", "default")
        return k8s_connector.check_pod_health(resource.id, pod_name, namespace)

    raise ValueError(f"Orchestrateur inconnu : {resource.orchestrator}")


@celery_app.task(name="app.services.health.poll_all_resources")
def poll_all_resources():
    """
    Tâche planifiée (toutes les 30s, voir beat_schedule) : vérifie la santé de
    toutes les ressources enregistrées et diffuse chaque résultat via WebSocket.
    """
    db = SessionLocal()
    results = []
    try:
        resources = db.query(Resource).all()
        for resource in resources:
            health = _check_single_resource(resource)
            results.append(health.model_dump(mode="json"))
            # La diffusion WebSocket réelle nécessite un pont sync->async ;
            # voir la note dans README des services pour l'implémentation
            # (ex: publier sur une file Redis pub/sub écoutée par le process ASGI).
    finally:
        db.close()
    return results
