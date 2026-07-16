# ThreatFusion

Plateforme développeur interne (IDP) self-service pour la gestion d'infrastructure.

ThreatFusion permet à un développeur d'enregistrer une ressource (service, app, DB), de la déployer, de surveiller sa santé en temps réel, et de garder une trace auditable de chaque action — le tout via une interface unique, sans dépendre d'une équipe ops.

## Stack

- **Backend** : FastAPI (REST + WebSocket)
- **Base de données** : PostgreSQL
- **Tâches asynchrones** : RabbitMQ + Celery
- **Frontend** : React + TypeScript
- **Documentation** : Fumadocs (TanStack Start)
- **Infra supervisée** : Docker / Kubernetes
- **Déploiement** : Docker Compose (one-command)

## Lancer le projet

```bash
cp .env.example .env
docker compose up --build
```

- Backend API : http://localhost:8000
- Documentation OpenAPI : http://localhost:8000/docs
- Frontend : http://localhost:3000
- Documentation : http://localhost:4000

## Structure du repo

```
backend/     API FastAPI, workers Celery, modèles, schémas
web/         Dashboard React with Tanstack Router
docs/        Fumadocs documentation site (architecture, ADR)
```

## Documentation

La documentation du projet est construite avec [Fumadocs](https://fumadocs.dev) :

```bash
pnpm dev:docs
```

Voir [`apps/docs/content/docs/architecture.mdx`](apps/docs/content/docs/architecture.mdx) pour le schéma complet et le cycle fonctionnel (enregistrement → monitoring → déploiement → audit).

## Décisions d'architecture

Voir [`apps/docs/content/docs/adr/`](apps/docs/content/docs/adr/) pour le détail et la justification des choix techniques.

## Statut

Projet en cours de développement
