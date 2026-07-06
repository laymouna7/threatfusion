"""
Instance Celery partagée par les workers et Celery beat.

Les tâches de déploiement (services/deployment.py) et de monitoring périodique
(services/health.py) sont enregistrées ici.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "threatfusion",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.beat_schedule = {
    "poll-infrastructure-health": {
        "task": "app.services.health.poll_all_resources",
        "schedule": 30.0,  # secondes
    },
}

# import app.services.deployment  # noqa -- enregistre les tâches de déploiement
# import app.services.health      # noqa -- enregistre les tâches de monitoring
