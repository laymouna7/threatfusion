"""
Schéma pivot de santé — reflète ADR 0003. Le connecteur Docker et le connecteur
Kubernetes traduisent tous les deux leur réponse native vers ce format avant
de le persister ou de le pousser au frontend via WebSocket.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

HealthStatus = Literal["healthy", "degraded", "down", "unknown"]


class ResourceHealth(BaseModel):
    resource_id: uuid.UUID
    status: HealthStatus
    orchestrator: Literal["docker", "kubernetes"]
    last_checked: datetime
    details: dict[str, Any] = {}
