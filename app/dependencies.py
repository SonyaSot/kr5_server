from __future__ import annotations
from fastapi import Header, HTTPException, Depends
from app.schemas import UserOut
from app.storage import TaskStorage, task_storage


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str = Header(default="user"),
) -> UserOut:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    return UserOut(id=user_id, role=x_user_role)


def require_admin(user: UserOut = Depends(get_current_user)) -> UserOut:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_storage() -> TaskStorage:
    return task_storage
