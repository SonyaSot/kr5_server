from __future__ import annotations
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from app.routers import tasks, users, admin
from app.schemas import HealthOut, RoomUsersOut
from app.ws_manager import room_manager

app = FastAPI(title="FastAPI КР5")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthOut, tags=["health"])
def health() -> HealthOut:
    return HealthOut(status="ok", env=os.getenv("APP_ENV", "local"))


# ── WebSocket chat rooms ──────────────────────────────────────────────────────
@app.websocket("/ws/rooms/{room_id}")
async def ws_room(
    websocket: WebSocket,
    room_id: str,
    username: str = Query(default=""),
) -> None:
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    username = username.strip()
    await room_manager.connect(room_id, username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                text: str = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json(
                        {"type": "error", "detail": "Message is too long"}
                    )
                else:
                    await room_manager.broadcast(
                        room_id,
                        {
                            "type": "message",
                            "room_id": room_id,
                            "username": username,
                            "text": text,
                        },
                    )
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username)


# ── Room info HTTP route ──────────────────────────────────────────────────────
@app.get("/rooms/{room_id}/users", response_model=RoomUsersOut, tags=["rooms"])
def room_users(room_id: str) -> RoomUsersOut:
    return RoomUsersOut(room_id=room_id, users=room_manager.get_users(room_id))
