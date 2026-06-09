"""WebSocket connection manager"""
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Aktiv WebSocket ulanishlarni boshqaradi."""

    def __init__(self):
        # user_id -> list[WebSocket] (bir user bir nechta tab ochishi mumkin)
        self.active: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active:
            self.active[user_id] = []
        self.active[user_id].append(websocket)
        logger.info(f"WS connected: user={user_id}, total={self._count()}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active:
            if websocket in self.active[user_id]:
                self.active[user_id].remove(websocket)
            if not self.active[user_id]:
                del self.active[user_id]
        logger.info(f"WS disconnected: user={user_id}")

    async def send_to_user(self, user_id: int, message: dict):
        """Foydalanuvchining hamma ulanishlariga yuborish."""
        for ws in self.active.get(user_id, []):
            await ws.send_json(message)

    def _count(self) -> int:
        return sum(len(v) for v in self.active.values())


# Global instance
manager = ConnectionManager()
