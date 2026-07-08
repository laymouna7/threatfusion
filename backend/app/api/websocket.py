"""
Endpoint WebSocket : pousse les mises à jour de statut de santé en temps réel
au frontend, sans qu'il ait à faire du polling HTTP.

Le ConnectionManager garde la liste des clients connectés ; les workers Celery
(services/health.py) appellent broadcast_health() après chaque poll pour
notifier tout le monde instantanément.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/health")
async def health_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Le client n'envoie rien en pratique ; on garde la connexion ouverte
            # et on reçoit juste pour détecter la déconnexion.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_health(health_update: dict):
    """Appelé par les workers Celery après un health-check pour notifier le frontend."""
    await manager.broadcast(health_update)
