# КР5 — Технологии разработки серверных приложений

Проект охватывает все 4 задания контрольной работы №5.

## Структура проекта

```
app/
  main.py          # точка входа, WebSocket-маршруты
  schemas.py       # Pydantic-модели
  storage.py       # in-memory хранилище задач
  dependencies.py  # get_current_user, require_admin, get_storage
  ws_manager.py    # RoomManager для WebSocket-комнат
  routers/
    tasks.py       # /tasks — CRUD задач
    users.py       # /users — профиль пользователя
    admin.py       # /admin — статистика и удаление
tests/
  conftest.py                        # фикстуры client и clear_storage
  test_tasks.py                      # Задание 1
  test_health.py                     # Задание 2
  test_websocket.py                  # Задание 3
  test_dependencies_and_routing.py   # Задание 4
Dockerfile
docker-compose.yml
.dockerignore
requirements.txt
```

---

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API доступно по адресу: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

---

## Запуск тестов

```bash
pytest
```

Или с подробным выводом:

```bash
pytest -v
```

---

## Запуск в Docker

```bash
docker compose up --build
```

Проверка:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
curl http://localhost:8000/health
```

---

## Авторизация

Все маршруты `/tasks`, `/users`, `/admin` требуют заголовок `X-User-Id`.  
Маршруты `/admin` дополнительно требуют `X-User-Role: admin`.

Пример:
```
X-User-Id: 10
X-User-Role: admin
```

---

