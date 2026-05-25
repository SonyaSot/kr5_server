from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Task schemas ──────────────────────────────────────────────────────────────

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus = "todo"
    priority: int = Field(..., ge=1, le=5)


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: int
    owner_id: int


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


# ── User schemas ──────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    role: str


# ── Admin schemas ─────────────────────────────────────────────────────────────

class AdminStats(BaseModel):
    total_tasks: int
    by_status: dict[str, int]


# ── Health ────────────────────────────────────────────────────────────────────

class HealthOut(BaseModel):
    status: str
    env: str


# ── WebSocket schemas ─────────────────────────────────────────────────────────

class WsMessage(BaseModel):
    type: Literal["message"]
    text: str


class RoomUsersOut(BaseModel):
    room_id: str
    users: list[str]
