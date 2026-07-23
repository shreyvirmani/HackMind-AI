from fastapi import WebSocket
from collections import defaultdict
import asyncio

class ConnectionManager:
    def __init__(self):
        self.connections = defaultdict(list)

    async def connect(self, workflow_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[workflow_id].append(websocket)

    def disconnect(self, workflow_id: str, websocket: WebSocket):
        if workflow_id in self.connections:
            if websocket in self.connections[workflow_id]:
                self.connections[workflow_id].remove(websocket)

            if len(self.connections[workflow_id]) == 0:
                del self.connections[workflow_id]

    async def send(self, workflow_id: str, event: dict):
        if workflow_id not in self.connections:
            return

        dead = []

        for ws in self.connections[workflow_id]:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(workflow_id, ws)


manager = ConnectionManager()