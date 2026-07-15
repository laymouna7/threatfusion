# ThreatFusion

Plateforme développeur interne (IDP) self-service pour la gestion d'infrastructure.

ThreatFusion permet à un développeur d'enregistrer une ressource (service, app, DB),
de la déployer, de surveiller sa santé en temps réel, et de garder une trace auditable
de chaque action — le tout via une interface unique, sans dépendre d'une équipe ops.

## Stack

- **Backend** : FastAPI (REST + WebSocket)
- **Base de données** : PostgreSQL
- **Tâches asynchrones** : RabbitMQ + Celery
- **Frontend** : React + TypeScript
- **Infra supervisée** : Docker / Kubernetes
- **Déploiement** : Docker Compose (one-command)

## Architecture

Voir [`docs/architecture.md`](docs/architecture.md) pour le schéma complet et le cycle
fonctionnel (enregistrement → monitoring → déploiement → audit).

## Lancer le projet

```bash
cp .env.example .env
docker compose up --build
```

- Backend API : http://localhost:8000
- Documentation OpenAPI : http://localhost:8000/docs
- Frontend : http://localhost:3000

## Structure du repo

```
backend/     API FastAPI, workers Celery, modèles, schémas
frontend/    Dashboard React/TypeScript
docs/        Architecture, ADR (Architecture Decision Records)
```

## Décisions d'architecture

Voir [`docs/adr/`](docs/adr/) pour le détail et la justification des choix techniques.

## Statut

🚧 Projet en cours de développement 

