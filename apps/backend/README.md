# ThreatFusion Backend

API FastAPI pour la plateforme IDP self-service ThreatFusion.

## Prérequis

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (gestionnaire de dépendances)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

```bash
cd apps/backend

# Installer toutes les dépendances (prod + dev)
uv sync --dev
```

## Lancement

```bash
# Depuis la racine du repo
pnpm dev:backend

# Ou directement
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

L'API est disponible sur http://localhost:8000.
La doc OpenAPI est disponible sur http://localhost:8000/docs.

## Tests

```bash
uv run pytest tests/ -v
```

Les tests utilisent SQLite (pas besoin de PostgreSQL).

## Variables d'environnement

```bash
cp .env.example .env
```

Éditer `.env` avec les credentials PostgreSQL, RabbitMQ et Redis.

## Déploiement Docker

```bash
# Depuis la racine du repo
docker compose -f infra/docker/docker-compose.yml up --build
```

Le Dockerfile utilise `uv` pour installer les dépendances sans cache.

## CI

Le pipeline GitHub Actions (`.github/workflows/test.yml`) exécute automatiquement les tests sur chaque PR et push vers `main`. Il utilise `astral-sh/setup-uv@v4` pour installer uv et `uv sync --dev` pour les dépendances.

## Structure

```
apps/backend/
├── app/              # Code application (routes, modèles, services)
├── tests/            # Tests pytest
├── scripts/          # Scripts utilitaires
├── pyproject.toml    # Dépendances et config projet
├── uv.lock           # Lock file
├── Dockerfile        # Image Docker de production
└── dev.sh            # Script de dev local
```
