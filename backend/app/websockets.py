from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    """
    Gère les connexions WebSocket actives par conversation.
    Chaque conversation a sa liste de connexions ouvertes.
    """

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        if conversation_id in self.active_connections:
            try:
                self.active_connections[conversation_id].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, conversation_id: int, data: dict):
        connections = self.active_connections.get(conversation_id, [])
        dead = []
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(conversation_id, d)


manager = ConnectionManager()
