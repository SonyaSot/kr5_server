import pytest
from fastapi.testclient import TestClient

USER_HEADERS = {"X-User-Id": "10"}
OTHER_HEADERS = {"X-User-Id": "99"}


def create_task(client: TestClient, title="Test task", priority=3, **kwargs):
    return client.post(
        "/tasks",
        json={"title": title, "priority": priority, **kwargs},
        headers=USER_HEADERS,
    )


# 1. Успешное создание задачи
def test_create_task_success(client):
    r = create_task(client, title="Подготовить тесты", priority=4,
                    description="Написать тесты", status="todo")
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Подготовить тесты"
    assert data["owner_id"] == 10
    assert data["id"] == 1


# 2. Ошибка 422, если title короче 3 символов
def test_create_task_short_title(client):
    r = create_task(client, title="ab", priority=1)
    assert r.status_code == 422


# 3. Ошибка 401, если нет заголовка X-User-Id
def test_create_task_no_auth(client):
    r = client.post("/tasks", json={"title": "Test task", "priority": 2})
    assert r.status_code == 401


# 4. Пользователь видит только свои задачи
def test_list_tasks_own_only(client):
    create_task(client, title="Task user 10", priority=1)
    client.post("/tasks", json={"title": "Task user 99", "priority": 1},
                headers=OTHER_HEADERS)
    r = client.get("/tasks", headers=USER_HEADERS)
    assert r.status_code == 200
    tasks = r.json()
    assert all(t["owner_id"] == 10 for t in tasks)
    assert len(tasks) == 1


# 5. Фильтрация задач по status и min_priority
def test_list_tasks_filter(client):
    create_task(client, title="Low prio todo", priority=1, status="todo")
    create_task(client, title="High prio done", priority=5, status="done")
    create_task(client, title="Mid prio in_progress", priority=3, status="in_progress")

    r = client.get("/tasks?status=done", headers=USER_HEADERS)
    assert len(r.json()) == 1
    assert r.json()[0]["status"] == "done"

    r = client.get("/tasks?min_priority=4", headers=USER_HEADERS)
    assert len(r.json()) == 1
    assert r.json()[0]["priority"] == 5


# 6. Успешное изменение статуса задачи
def test_update_status(client):
    create_task(client)
    r = client.patch("/tasks/1/status", json={"status": "done"}, headers=USER_HEADERS)
    assert r.status_code == 200
    assert r.json()["status"] == "done"


# 7. Ошибка 404 при обращении к чужой или несуществующей задаче
def test_get_task_not_found(client):
    r = client.get("/tasks/999", headers=USER_HEADERS)
    assert r.status_code == 404


def test_get_task_other_user(client):
    client.post("/tasks", json={"title": "Other task", "priority": 2},
                headers=OTHER_HEADERS)
    r = client.get("/tasks/1", headers=USER_HEADERS)
    assert r.status_code == 404


# 8. Успешное удаление задачи
def test_delete_task(client):
    create_task(client)
    r = client.delete("/tasks/1", headers=USER_HEADERS)
    assert r.status_code == 204
    r = client.get("/tasks/1", headers=USER_HEADERS)
    assert r.status_code == 404
