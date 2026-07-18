"""Schéma Pydantic pour le journal d'audit."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resource_id: uuid.UUID
    action: str
    actor: str | None
    details: dict[str, Any]
    created_at: datetime
