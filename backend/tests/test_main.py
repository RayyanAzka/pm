from fastapi.testclient import TestClient

import app.main as main

client = TestClient(main.app)


def test_root_serves_html() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text


def test_health_route() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pm-backend"}


def test_hello_route() -> None:
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from PM backend"}


def test_user_board_defaults_and_persists(tmp_path) -> None:
    main.DATABASE_PATH = tmp_path / "part6.db"
    main.init_db()

    response = client.get("/api/users/user/board")
    assert response.status_code == 200
    payload = response.json()
    assert payload["columns"][0]["title"] == "Backlog"
    assert payload["cards"]

    board_update = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
            {"id": "col-discovery", "title": "Discovery", "cardIds": []},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "First task", "details": "Persisted"}
        },
    }

    update_response = client.put("/api/users/user/board", json=board_update)
    assert update_response.status_code == 200
    stored = client.get("/api/users/user/board")
    assert stored.json()["cards"]["card-1"]["title"] == "First task"


def test_ai_route_requires_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    response = client.post("/api/ai/test", json={"prompt": "2+2"})

    assert response.status_code == 500
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


def test_ai_route_returns_response(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def fake_call(prompt: str) -> str:
        assert prompt == "2+2"
        return "4"

    monkeypatch.setattr(main, "call_openrouter", fake_call)

    response = client.post("/api/ai/test", json={"prompt": "2+2"})

    assert response.status_code == 200
    assert response.json()["response"] == "4"
