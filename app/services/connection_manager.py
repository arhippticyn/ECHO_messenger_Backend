from fastapi import WebSocket

class ConnectionMessage:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)


    def disconnect(self, chat_id: int, websocket):
        self.active_connections[chat_id].remove(websocket)
        if not self.active_connections[chat_id]:
            del self.active_connections[chat_id]


    async def broadcast(self, chat_id, message: dict):
        connections = self.active_connections.get(chat_id, [])
        dead_connections = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        
        for dead in dead_connections:
            connections.remove(dead)


manager = ConnectionMessage()