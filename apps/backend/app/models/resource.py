"""
Modèle d'une ressource enregistrée (service, app, DB) supervisée par ThreatFusion.

Une ressource possède un historique de déploiements et un journal d'audit
(relations définies dans deployment.py et audit_log.py).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)  # ex: "api", "worker", "database"
    orchestrator = Column(String, nullable=False)  # "docker" | "kubernetes"
    config = Column(JSON, nullable=False, default=dict)  # image, env vars, etc.

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    deployments = relationship("Deployment", back_populates="resource", cascade="all, delete-orphan")
    audit_entries = relationship("AuditLog", back_populates="resource", cascade="all, delete-orphan")
