"""
Point d'entrée FastAPI de ThreatFusion.

Assemble les routers REST et l'endpoint WebSocket. Chaque domaine (ressources,
déploiements, audit, santé) vit dans son propre router sous app/api/.

Au démarrage, lance aussi le pont Redis -> WebSocket (voir services/realtime.py) :
c'est ce qui permet aux mises à jour de santé calculées par les workers Celery
d'atteindre les clients connectés en temps réel.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, deployments, resources, websocket
from app.api.websocket import manager
from app.core.config import settings
from app.db.session import Base, engine
from app.services.realtime import redis_subscriber_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crée les tables (resources, deployments, audit_log) si elles n'existent
    # pas encore. Solution rapide pour l'instant ; Alembic (déjà en dépendance)
    # serait la bonne approche pour de vraies migrations versionnées.
    Base.metadata.create_all(bind=engine)

    subscriber_task = asyncio.create_task(redis_subscriber_loop(manager.broadcast))
    yield
    subscriber_task.cancel()


app = FastAPI(
    title="ThreatFusion",
    description="Plateforme développeur interne (IDP) self-service pour la gestion d'infrastructure.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Healthcheck basique de l'API elle-même (pas de l'infra supervisée)."""
    return {"status": "ok"}


app.include_router(resources.router, prefix="/resources", tags=["resources"])
app.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(websocket.router, tags=["websocket"])