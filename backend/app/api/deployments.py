"""
Router REST pour déclencher et consulter les déploiements.

C'est l'étape "Déploiement" du cycle fonctionnel : POST /deployments/ ne fait
QUE créer l'entrée en base et envoyer la tâche dans la file Celery — le travail
réel (appel Docker/K8s) se passe dans un worker, de façon asynchrone. Voir
ADR 0002 pour la justification.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.deployment import Deployment
from app.models.resource import Resource
from app.schemas.deployment import DeploymentOut
from app.services.deployment import run_deployment

router = APIRouter()


@router.post("/{resource_id}", response_model=DeploymentOut, status_code=202)
def trigger_deployment(resource_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Déclenche un déploiement. Retourne immédiatement (202 Accepted) avec le
    déploiement en statut 'pending' — le frontend suit son évolution via
    WebSocket, pas en attendant cette réponse.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ressource introuvable")

    deployment = Deployment(resource_id=resource.id, status="pending")
    db.add(deployment)
    db.flush()

    task = run_deployment.delay(str(deployment.id))
    deployment.celery_task_id = task.id

    db.add(
        AuditLog(
            resource_id=resource.id,
            action="deployment_triggered",
            actor="system",
            details={"deployment_id": str(deployment.id)},
        )
    )
    db.commit()
    db.refresh(deployment)
    return deployment


@router.get("/{resource_id}", response_model=list[DeploymentOut])
def list_deployments(resource_id: uuid.UUID, db: Session = Depends(get_db)):
    """Historique des déploiements d'une ressource, plus récent en premier."""
    return (
        db.query(Deployment)
        .filter(Deployment.resource_id == resource_id)
        .order_by(Deployment.started_at.desc())
        .all()
    )
