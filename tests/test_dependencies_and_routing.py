
USER_H = {"X-User-Id": "10", "X-User-Role": "user"}
ADMIN_H = {"X-User-Id": "1", "X-User-Role": "admin"}
OTHER_H = {"X-User-Id": "99", "X-User-Role": "user"}


def _create_task(client, headers=USER_H, title="Task", priority=2):
    return client.post("/tasks", json={"title": title, "priority": priority},
                       headers=headers)


# 1. /users/me возвращает текущего пользователя
def test_users_me(client):
    r = client.get("/users/me", headers=USER_H)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == 10
    assert data["role"] == "user"


# 2. Пользователь без X-User-Id получает 401
def test_users_me_no_auth(client):
    r = client.get("/users/me")
    assert r.status_code == 401


# 3. Обычный пользователь получает 403 при обращении к /admin/stats
def test_admin_stats_forbidden_for_user(client):
    r = client.get("/admin/stats", headers=USER_H)
    assert r.status_code == 403


# 4. Администратор получает статистику по всем задачам
def test_admin_stats(client):
    _create_task(client, headers=USER_H, title="Task one")
    _create_task(client, headers=OTHER_H, title="Task two")
    r = client.get("/admin/stats", headers=ADMIN_H)
    assert r.status_code == 200
    data = r.json()
    assert data["total_tasks"] == 2
    assert "by_status" in data


# 5. Обычный пользователь не может удалить чужую задачу через /tasks/{task_id}
def test_user_cannot_delete_others_task(client):
    _create_task(client, headers=OTHER_H, title="Other task")
    r = client.delete("/tasks/1", headers=USER_H)
    assert r.status_code == 404  # not found from user's perspective


# 6. Администратор может удалить чужую задачу через /admin/tasks/{task_id}
def test_admin_can_delete_any_task(client):
    _create_task(client, headers=USER_H, title="Some task")
    r = client.delete("/admin/tasks/1", headers=ADMIN_H)
    assert r.status_code == 204


# 7. Swagger UI — маршруты сгруппированы по тегам (проверяем openapi schema)
def test_swagger_tags(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    tags_found = set()
    for path_item in paths.values():
        for op in path_item.values():
            if isinstance(op, dict):
                tags_found.update(op.get("tags", []))
    assert "tasks" in tags_found
    assert "users" in tags_found
    assert "admin" in tags_found
