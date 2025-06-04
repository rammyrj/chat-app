from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .database import db
from .models import Message

router = APIRouter()
connections = {}

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connections[username] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            msg = Message(**data)
            await db.messages.insert_one(msg.dict())
            if msg.receiver in connections:
                await connections[msg.receiver].send_json(msg.dict())
    except WebSocketDisconnect:
        del connections[username]
