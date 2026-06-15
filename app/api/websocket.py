"""
WebSocket handlers — real-time chat and agent log streaming.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.refund_service import process_refund
from app.services.auth_service import decode_access_token

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        if channel in self.active_connections:
            self.active_connections[channel] = [
                ws for ws in self.active_connections[channel] if ws != websocket
            ]

    async def broadcast(self, message: dict, channel: str = "default"):
        if channel in self.active_connections:
            dead = []
            for ws in self.active_connections[channel]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, channel)


manager = ConnectionManager()


@router.websocket("/chat")
async def chat_websocket(websocket: WebSocket):
    """
    Customer chat WebSocket.

    Client sends: {"message": "...", "customer_id": int?, "order_number": str?, "token": str}
    Server streams back:
      - {"type": "agent_log", "data": {...}} for each agent step
      - {"type": "result", "data": {...}} for the final decision
      - {"type": "error", "data": {"message": "..."}} on errors
    """
    await manager.connect(websocket, "chat")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            message = data.get("message", "")
            customer_id = data.get("customer_id")
            order_number = data.get("order_number")
            token = data.get("token")

            # Optional token validation
            db = SessionLocal()
            try:
                if token:
                    payload = decode_access_token(token)
                    if not payload:
                        await websocket.send_json({"type": "error", "data": {"message": "Invalid token"}})
                        continue
                    
                    # Find user and customer
                    from app.db.models import User, Customer
                    user = db.query(User).filter(User.id == int(payload.get("sub", 0))).first()
                    if user:
                        customer = db.query(Customer).filter(Customer.email == user.email).first()
                        if customer:
                            customer_id = customer.id

                if not message:
                    await websocket.send_json({"type": "error", "data": {"message": "Message is required"}})
                    continue

                # Echo back the user message
                await websocket.send_json({
                    "type": "user_message",
                    "data": {"message": message},
                })

                # Agent log callback — streams reasoning in real-time
                async def on_agent_log(log_entry: dict):
                    await websocket.send_json({
                        "type": "agent_log",
                        "data": log_entry,
                    })
                    # Also broadcast to the logs channel
                    await manager.broadcast(
                        {"type": "agent_log", "data": log_entry},
                        channel="logs",
                    )

                # Run the refund workflow
                result = await process_refund(
                    db=db,
                    customer_message=message,
                    customer_id=customer_id,
                    order_number=order_number,
                    on_agent_log=on_agent_log,
                )

                await websocket.send_json({
                    "type": "result",
                    "data": result,
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Workflow error: {str(e)}"},
                })
            finally:
                db.close()

    except WebSocketDisconnect:
        manager.disconnect(websocket, "chat")
    except Exception:
        manager.disconnect(websocket, "chat")


@router.websocket("/logs/{request_id}")
async def logs_websocket(websocket: WebSocket, request_id: str):
    """
    Agent log streaming WebSocket for a specific request.
    Broadcasts agent reasoning logs in real-time as they're produced.
    """
    channel = f"logs_{request_id}"
    await manager.connect(websocket, channel)

    try:
        while True:
            # Keep alive — client can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
    except Exception:
        manager.disconnect(websocket, channel)


@router.websocket("/logs")
async def all_logs_websocket(websocket: WebSocket):
    """Stream all agent logs across all requests — for the Agent Logs page."""
    await manager.connect(websocket, "logs")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "logs")
    except Exception:
        manager.disconnect(websocket, "logs")
