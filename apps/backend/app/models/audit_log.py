"""
Journal d'audit : trace chaque action significative sur une ressource
(enregistrement, déploiement déclenché, changement de statut de santé).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)

    action = Column(String, nullable=False)  # ex: "resource_created", "deployment_triggered"
    actor = Column(String, nullable=True)  # utilisateur ou "system"
    details = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resource = relationship("Resource", back_populates="audit_entries")
