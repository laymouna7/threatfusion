"""Schémas Pydantic : contrat d'entrée/sortie de l'API pour les ressources."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResourceCreate(BaseModel):
    name: str
    type: str
    orchestrator: str  # "docker" | "kubernetes"
    config: dict[str, Any] = {}


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    orchestrator: str
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime
