# ADR 0002 : Celery + RabbitMQ plutôt qu'une planification cron simple

## Statut
Accepté

## Contexte
Deux besoins asynchrones : (1) exécuter un déploiement à la demande sans bloquer
l'API, (2) vérifier périodiquement la santé de l'infrastructure.

## Décision
RabbitMQ comme broker de messages, Celery comme moteur de tâches (workers +
Celery beat pour la planification), plutôt qu'un simple cron ou des tâches
`BackgroundTasks` de FastAPI.

## Justification
- **Déploiement à la demande** : besoin d'une file de tâches persistante, pas
  d'un simple thread en arrière-plan — si le worker crashe, la tâche ne doit pas
  être perdue
- **Scalabilité** : plusieurs workers peuvent traiter les déploiements en
  parallèle si plusieurs ressources sont déployées simultanément
- **Monitoring périodique** : Celery beat centralise la planification, plus
  robuste qu'un cron externe au conteneur applicatif
- **Traçabilité** : Celery permet de suivre l'état d'une tâche (pending, started,
  success, failure), directement exploitable pour l'audit

## Conséquences
- Ajoute un composant d'infrastructure supplémentaire (RabbitMQ) à opérer et
  monitorer
- Complexité de configuration initiale plus élevée qu'un simple cron
