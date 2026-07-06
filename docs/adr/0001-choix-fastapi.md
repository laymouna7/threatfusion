# ADR 0001 : choix de FastAPI comme framework backend

## Statut
Accepté

## Contexte
Le backend doit exposer une API REST, un endpoint WebSocket pour le temps réel,
et générer une documentation technique (OpenAPI) exploitable sans effort
supplémentaire.

## Décision
FastAPI est retenu plutôt que Flask ou Django.

## Justification
- Support natif de WebSocket et de l'async (nécessaire pour interroger Docker/K8s
  sans bloquer l'API pendant les I/O)
- Génération automatique de la documentation OpenAPI à partir du code (routes,
  schémas Pydantic) — répond directement à l'exigence de documentation technique
- Validation des données entrantes/sortantes via Pydantic, réduit les erreurs de
  contrat d'API
- Performances supérieures à Flask/Django pour des charges I/O-bound comme
  l'agrégation de santé multi-source

## Conséquences
- Nécessite une bonne maîtrise de l'async Python (async/await) pour éviter de
  bloquer l'event loop par erreur
- Écosystème plus jeune que Django (moins de packages "batteries incluses"),
  compensé ici par des besoins ciblés (pas d'admin panel, pas d'ORM imposé)
