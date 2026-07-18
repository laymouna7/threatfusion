"""
Router REST pour l'enregistrement et la consultation des ressources.

C'est l'étape "Enregistrement" du cycle fonctionnel : le développeur déclare
une ressource, elle est persistée, puis surveillée automatiquement.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceOut

router = APIRouter()


@router.post("/", response_model=ResourceOut, status_code=201)
def register_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    """Enregistre une nouvelle ressource et journalise l'action dans l'audit."""
    existing = db.query(Resource).filter(Resource.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Une ressource avec ce nom existe déjà")

    resource = Resource(**payload.model_dump())
    db.add(resource)
    db.flush()  # récupère resource.id avant commit

    db.add(
        AuditLog(
            resource_id=resource.id,
            action="resource_created",
            actor="system",
            details={"name": resource.name, "orchestrator": resource.orchestrator},
        )
    )
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db)):
    """Liste toutes les ressources enregistrées (pour le dashboard)."""
    return db.query(Resource).order_by(Resource.created_at.desc()).all()


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(resource_id: uuid.UUID, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ressource introuvable")
    return resource


@router.delete("/{resource_id}", status_code=204)
def delete_resource(resource_id: uuid.UUID, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ressource introuvable")
    db.delete(resource)
    db.commit()
