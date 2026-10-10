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


def test_openrouter_requests_sufficient_json_completion(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    request_data = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "{}"}}]}

    def fake_post(url: str, **kwargs):
        request_data.update(kwargs["json"])
        return FakeResponse()

    monkeypatch.setattr(main.httpx, "post", fake_post)

    assert main.call_openrouter("Return JSON") == "{}"
    assert request_data["max_tokens"] >= 2048
    assert request_data["response_format"] == {"type": "json_object"}


def test_ai_board_route_accepts_valid_update(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    fake_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Original", "details": "Before"},
        },
    }

    def fake_call(prompt: str) -> str:
        assert "Original" in prompt
        return '{"response": "Updated the task title.", "board": {"columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]}], "cards": {"card-1": {"id": "card-1", "title": "Updated", "details": "After"}}}}'

    monkeypatch.setattr(main, "call_openrouter", fake_call)

    response = client.post(
        "/api/ai/board",
        json={
            "username": "user",
            "prompt": "Rename the task from Original to Updated.",
            "board": fake_board,
            "history": [{"role": "user", "content": "hello"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Updated the task title."
    assert response.json()["board"]["cards"]["card-1"]["title"] == "Updated"


def test_ai_board_route_rejects_invalid_update(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    fake_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Original", "details": "Before"},
        },
    }

    def fake_call(prompt: str) -> str:
        assert "Original" in prompt
        return '{"response": "I cannot do that.", "board": {"columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-2"]}], "cards": {}}}'

    monkeypatch.setattr(main, "call_openrouter", fake_call)

    response = client.post(
        "/api/ai/board",
        json={
            "username": "user",
            "prompt": "Rename the task from Original to Updated.",
            "board": fake_board,
        },
    )

    assert response.status_code == 400
    assert "board" in response.json()["detail"].lower()


def test_ai_board_route_accepts_markdown_wrapped_json(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    fake_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Original", "details": "Before"},
        },
    }

    def fake_call(prompt: str) -> str:
        assert "Original" in prompt
        return '''```json
{"response": "Updated the task title.", "board": {"columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]}], "cards": {"card-1": {"id": "card-1", "title": "Updated", "details": "After"}}}}
```'''

    monkeypatch.setattr(main, "call_openrouter", fake_call)

    response = client.post(
        "/api/ai/board",
        json={
            "username": "user",
            "prompt": "Rename the task from Original to Updated.",
            "board": fake_board,
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Updated the task title."
    assert response.json()["board"]["cards"]["card-1"]["title"] == "Updated"


def test_ai_board_route_recovers_missing_commas_in_json(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    fake_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Original", "details": "Before"},
            "card-2": {"id": "card-2", "title": "Hold", "details": "Pending"},
        },
    }

    def fake_call(prompt: str) -> str:
        assert "Original" in prompt
        return '{"response": "Updated the task title.", "board": {"columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]}], "cards": {"card-1": {"id": "card-1", "title": "Updated", "details": "After"}"card-2": {"id": "card-2", "title": "Hold", "details": "Pending"}}}}'

    monkeypatch.setattr(main, "call_openrouter", fake_call)

    response = client.post(
        "/api/ai/board",
        json={
            "username": "user",
            "prompt": "Rename the task from Original to Updated.",
            "board": fake_board,
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Updated the task title."
    assert response.json()["board"]["cards"]["card-1"]["title"] == "Updated"
