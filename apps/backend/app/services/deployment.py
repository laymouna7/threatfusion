"""
Tâche Celery de déploiement : c'est le travail réel déclenché par
POST /deployments/{resource_id} (voir api/deployments.py). Tourne dans un
worker séparé, jamais dans le process de l'API.
"""

from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.deployment import Deployment
from app.services import docker_connector
from app.workers.celery_app import celery_app


@celery_app.task(name="app.services.deployment.run_deployment", bind=True, max_retries=2)
def run_deployment(self, deployment_id: str):
    """
    Exécute un déploiement : lit la ressource associée, lance le conteneur via
    le connecteur adapté, met à jour le statut en base, journalise le résultat.
    """
    db = SessionLocal()
    try:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            return {"error": "déploiement introuvable"}

        deployment.status = "running"
        db.commit()

        resource = deployment.resource
        try:
            if resource.orchestrator == "docker":
                image = resource.config.get("image")
                if not image:
                    raise ValueError("config.image manquant pour une ressource docker")
                container_id = docker_connector.deploy_container(
                    image=image,
                    name=resource.config.get("container_name", resource.name),
                    env=resource.config.get("env"),
                )
                deployment.status = "succeeded"
                deployment.finished_at = datetime.now(timezone.utc)
                db.add(
                    AuditLog(
                        resource_id=resource.id,
                        action="deployment_succeeded",
                        actor="system",
                        details={"deployment_id": str(deployment.id), "container_id": container_id},
                    )
                )
            else:
                # Kubernetes : le déploiement se fait typiquement via un manifest
                # (Deployment/Pod spec) plutôt qu'un simple "run" — à implémenter
                # selon le format de config choisi pour les ressources K8s.
                raise NotImplementedError("Déploiement Kubernetes pas encore implémenté")

        except Exception as e:
            deployment.status = "failed"
            deployment.error_message = str(e)
            deployment.finished_at = datetime.now(timezone.utc)
            db.add(
                AuditLog(
                    resource_id=resource.id,
                    action="deployment_failed",
                    actor="system",
                    details={"deployment_id": str(deployment.id), "error": str(e)},
                )
            )

        db.commit()
        return {"deployment_id": str(deployment.id), "status": deployment.status}
    finally:
        db.close()
