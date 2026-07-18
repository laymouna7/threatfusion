"""
Pont Redis pub/sub entre Celery (process séparé) et le serveur FastAPI/WebSocket.

Le problème que ça résout : quand un worker Celery termine un health-check
(services/health.py), il tourne dans un process complètement différent du
serveur FastAPI qui gère les connexions WebSocket. Un worker ne peut pas
"appeler" directement ConnectionManager.broadcast() du serveur — ce sont deux
programmes séparés, potentiellement sur deux machines différentes.

La solution : Redis pub/sub sert d'intermédiaire.
  1. Le worker Celery PUBLIE le résultat sur un canal Redis (publish_health_update).
  2. Le serveur FastAPI, au démarrage, lance une tâche de fond qui S'ABONNE à ce
     canal (redis_subscriber_loop) et relaie chaque message reçu vers tous les
     clients WebSocket connectés via ConnectionManager.

Voir ADR 0004 pour la justification de Redis plutôt qu'une autre approche.
"""

import json

import redis as redis_sync
import redis.asyncio as redis_async

from app.core.config import settings

HEALTH_CHANNEL = "threatfusion:health_updates"


def publish_health_update(health_data: dict) -> None:
    """
    Appelé côté Celery (process worker, code SYNCHRONE) après un health-check.
    Publie le résultat sur Redis ; ne lève jamais d'exception vers l'appelant
    pour ne pas faire échouer la tâche de monitoring si Redis est indisponible.
    """
    try:
        client = redis_sync.from_url(settings.redis_url)
        client.publish(HEALTH_CHANNEL, json.dumps(health_data))
    except redis_sync.RedisError:
        # Le monitoring doit continuer même si la diffusion temps réel échoue ;
        # le prochain poll (30s plus tard) retentera.
        pass


async def redis_subscriber_loop(broadcast_callback):
    """
    Appelé côté FastAPI (process serveur, code ASYNCHRONE) au démarrage de l'app.
    Tourne en tâche de fond pendant toute la vie du serveur : écoute Redis et
    relaie chaque message reçu à `broadcast_callback` (ConnectionManager.broadcast).
    """
    client = redis_async.from_url(settings.redis_url)
    pubsub = client.pubsub()
    await pubsub.subscribe(HEALTH_CHANNEL)

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                health_data = json.loads(message["data"])
                await broadcast_callback(health_data)
            except (json.JSONDecodeError, KeyError):
                continue
    finally:
        await pubsub.unsubscribe(HEALTH_CHANNEL)
        await client.aclose()
