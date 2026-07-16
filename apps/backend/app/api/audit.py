"""Router REST pour consulter le journal d'audit (étape 'Audit' du cycle)."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogOut

router = APIRouter()


@router.get("/{resource_id}", response_model=list[AuditLogOut])
def get_audit_trail(resource_id: uuid.UUID, db: Session = Depends(get_db)):
    """Historique complet des actions sur une ressource, plus récent en premier."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.resource_id == resource_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
