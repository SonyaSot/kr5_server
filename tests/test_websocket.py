from fastapi.testclient import TestClient


# 1. Подключение к комнате с корректным username
def test_ws_connect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "join"
        assert msg["username"] == "alice"
        assert msg["room_id"] == "python"


# 2. Отправка сообщения и получение ответа через WebSocket
def test_ws_send_receive(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join event
        ws.send_json({"type": "message", "text": "Привет"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["text"] == "Привет"
        assert msg["username"] == "alice"


# 3. Два клиента в одной комнате получают одно и то же сообщение
def test_ws_broadcast(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_a:
        ws_a.receive_json()  # alice join
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws_b:
            ws_a.receive_json()  # bob join (received by alice)
            ws_b.receive_json()  # bob join (received by bob)
            ws_a.send_json({"type": "message", "text": "Hello all"})
            msg_a = ws_a.receive_json()
            msg_b = ws_b.receive_json()
            assert msg_a["text"] == msg_b["text"] == "Hello all"


# 4. Пользователи из разных комнат не получают чужие сообщения
def test_ws_different_rooms_isolation(client):
    import threading, queue

    results: queue.Queue = queue.Queue()

    def bob_session():
        with client.websocket_connect("/ws/rooms/other?username=bob") as ws_b:
            ws_b.receive_json()  # own join event
            results.put("ready")
            # bob waits — if he gets another message, put it
            try:
                ws_b.receive_json(timeout=0.5)
                results.put("received_extra")
            except Exception:
                results.put("no_extra")

    t = threading.Thread(target=bob_session, daemon=True)
    t.start()

    assert results.get(timeout=2) == "ready"

    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_a:
        ws_a.receive_json()
        ws_a.send_json({"type": "message", "text": "Only python room"})
        ws_a.receive_json()  # alice gets own broadcast

    t.join(timeout=2)
    assert results.get(timeout=2) == "no_extra"


# 5. Слишком длинное сообщение возвращает событие error
def test_ws_long_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # join
        ws.send_json({"type": "message", "text": "x" * 301})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert "too long" in msg["detail"].lower()


# 6. После отключения пользователя маршрут /rooms/{room_id}/users не возвращает его
def test_ws_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/python?username=alice"):
        pass  # disconnects on exit

    r = client.get("/rooms/python/users")
    assert r.status_code == 200
    assert "alice" not in r.json()["users"]
