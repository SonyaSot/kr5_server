from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import TaskCreate, TaskOut, TaskStatusUpdate, UserOut
from app.dependencies import get_current_user, get_storage
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    user: UserOut = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> TaskOut:
    return storage.create({**body.model_dump(), "owner_id": user.id})


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    user: UserOut = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> list[TaskOut]:
    return storage.list_by_owner(user.id, status=status, min_priority=min_priority)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    user: UserOut = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> TaskOut:
    task = storage.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    user: UserOut = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> TaskOut:
    task = storage.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.update_status(task_id, body.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user: UserOut = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
) -> None:
    task = storage.get(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.delete(task_id)
