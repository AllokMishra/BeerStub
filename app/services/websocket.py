from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from ..models import DispenserMachine

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.machine_status: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")

    async def broadcast_machine_status(self, machine: DispenserMachine):
        message = {
            "machine_id": machine.id,
            "device_id": machine.device_id,
            "is_online": machine.is_online,
            "last_seen": machine.last_seen.isoformat() if machine.last_seen else None
        }
        
        for connection in self.active_connections.values():
            try:
                await connection.send_json({
                    "type": "machine_status",
                    "data": message
                })
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")

    async def handle_websocket(self, websocket: WebSocket, client_id: str):
        await self.connect(websocket, client_id)
        try:
            while True:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
        except WebSocketDisconnect:
            self.disconnect(client_id)

websocket_manager = WebSocketManager()