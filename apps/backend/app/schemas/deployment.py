"""Schémas Pydantic pour les déploiements."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeploymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resource_id: uuid.UUID
    status: str
    celery_task_id: str | None
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None
