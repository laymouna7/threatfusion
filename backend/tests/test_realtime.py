"""
Teste la logique du pont Redis sans avoir besoin d'un vrai serveur Redis :
on mocke le client et on vérifie que publish/subscribe font ce qu'il faut,
et surtout que les erreurs Redis ne remontent jamais vers l'appelant.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis as redis_sync

from app.services.realtime import HEALTH_CHANNEL, publish_health_update, redis_subscriber_loop


def test_publish_health_update_calls_redis_publish():
    fake_client = MagicMock()
    with patch("app.services.realtime.redis_sync.from_url", return_value=fake_client):
        publish_health_update({"status": "healthy", "resource_id": "abc"})

    fake_client.publish.assert_called_once()
    channel, payload = fake_client.publish.call_args[0]
    assert channel == HEALTH_CHANNEL
    assert "healthy" in payload


def test_publish_health_update_swallows_redis_errors():
    fake_client = MagicMock()
    fake_client.publish.side_effect = redis_sync.RedisError("connexion refusée")

    with patch("app.services.realtime.redis_sync.from_url", return_value=fake_client):
        # Ne doit lever aucune exception : le monitoring doit continuer.
        publish_health_update({"status": "down"})


@pytest.mark.asyncio
async def test_subscriber_loop_forwards_messages_to_callback():
    fake_pubsub = MagicMock()
    fake_pubsub.subscribe = AsyncMock()
    fake_pubsub.unsubscribe = AsyncMock()

    async def fake_listen():
        yield {"type": "subscribe", "data": 1}  # message de confirmation, doit être ignoré
        yield {"type": "message", "data": '{"status": "healthy", "resource_id": "abc"}'}

    fake_pubsub.listen = fake_listen

    fake_client = MagicMock()
    fake_client.pubsub.return_value = fake_pubsub
    fake_client.aclose = AsyncMock()

    received = []

    async def fake_callback(data):
        received.append(data)
        raise StopAsyncIteration  # arrête la boucle après le premier message utile

    with patch("app.services.realtime.redis_async.from_url", return_value=fake_client):
        try:
            await redis_subscriber_loop(fake_callback)
        except StopAsyncIteration:
            pass

    assert received == [{"status": "healthy", "resource_id": "abc"}]
