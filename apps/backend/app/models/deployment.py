"""
Modèle d'un déploiement : une exécution (réussie ou non) d'une ressource sur
Docker/Kubernetes, déclenchée via une tâche Celery.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)

    # pending -> running -> succeeded | failed
    status = Column(String, nullable=False, default="pending")
    celery_task_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime(timezone=True), nullable=True)

    resource = relationship("Resource", back_populates="deployments")
