from __future__ import annotations
from typing import Optional
from app.schemas import TaskOut


class TaskStorage:
    """Simple in-memory task storage."""

    def __init__(self) -> None:
        self._tasks: dict[int, TaskOut] = {}
        self._counter: int = 0

    def create(self, data: dict) -> TaskOut:
        self._counter += 1
        task = TaskOut(id=self._counter, **data)
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Optional[TaskOut]:
        return self._tasks.get(task_id)

    def list_by_owner(
        self,
        owner_id: int,
        status: Optional[str] = None,
        min_priority: Optional[int] = None,
    ) -> list[TaskOut]:
        result = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status:
            result = [t for t in result if t.status == status]
        if min_priority is not None:
            result = [t for t in result if t.priority >= min_priority]
        return result

    def update_status(self, task_id: int, status: str) -> Optional[TaskOut]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        self._tasks[task_id] = task.model_copy(update={"status": status})
        return self._tasks[task_id]

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def all_tasks(self) -> list[TaskOut]:
        return list(self._tasks.values())

    def clear(self) -> None:
        self._tasks.clear()
        self._counter = 0


# Singleton used by the app; tests can replace it via dependency override
task_storage = TaskStorage()
