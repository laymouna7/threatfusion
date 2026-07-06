"""
Point d'entrée FastAPI de ThreatFusion.

Assemble les routers REST et l'endpoint WebSocket. Chaque domaine (ressources,
déploiements, audit, santé) vit dans son propre router sous app/api/.
"""

from fastapi import FastAPI

app = FastAPI(
    title="ThreatFusion",
    description="Plateforme développeur interne (IDP) self-service pour la gestion d'infrastructure.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Healthcheck basique de l'API elle-même (pas de l'infra supervisée)."""
    return {"status": "ok"}


# Routers à brancher au fur et à mesure :
# from app.api import resources, deployments, audit, websocket
# app.include_router(resources.router, prefix="/resources", tags=["resources"])
# app.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
# app.include_router(audit.router, prefix="/audit", tags=["audit"])
# app.include_router(websocket.router, tags=["websocket"])
