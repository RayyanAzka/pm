import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PM Backend", version="0.1.0")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "out"
FALLBACK_STATIC_DIR = Path(__file__).resolve().parent / "static"
DATABASE_PATH = Path(os.getenv("PM_DATABASE_PATH", PROJECT_ROOT / "data" / "pm.db"))
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect_db() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _default_board() -> dict:
    return {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
            {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
            {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
            {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
            {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
            "card-2": {"id": "card-2", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
            "card-3": {"id": "card-3", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
            "card-4": {"id": "card-4", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
            "card-5": {"id": "card-5", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
            "card-6": {"id": "card-6", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
            "card-7": {"id": "card-7", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
            "card-8": {"id": "card-8", "title": "Close onboarding sprint", "details": "Document release notes and share internally."},
        },
    }


def init_db() -> None:
    connection = _connect_db()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL DEFAULT 'Project Board',
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS columns (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                title TEXT NOT NULL,
                FOREIGN KEY (board_id) REFERENCES boards(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                column_id TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (board_id) REFERENCES boards(id),
                FOREIGN KEY (column_id) REFERENCES columns(id)
            )
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
            ("user-1", "user", "password", utc_now()),
        )
        connection.commit()
    finally:
        connection.close()


def _get_user_id(username: str) -> str:
    connection = _connect_db()
    try:
        row = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row is not None:
            return row["id"]

        user_id = f"user-{len(connection.execute('SELECT id FROM users').fetchall()) + 1}"
        connection.execute(
            "INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (user_id, username, "password", utc_now()),
        )
        connection.commit()
        return user_id
    finally:
        connection.close()


def _ensure_board_for_user(user_id: str) -> str:
    connection = _connect_db()
    try:
        row = connection.execute(
            "SELECT id FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row is not None:
            return row["id"]

        board_id = f"board-{user_id}"
        connection.execute(
            "INSERT INTO boards (id, user_id, name, updated_at) VALUES (?, ?, ?, ?)",
            (board_id, user_id, "Project Board", utc_now()),
        )
        default_board = _default_board()
        for column_index, column in enumerate(default_board["columns"]):
            connection.execute(
                "INSERT INTO columns (id, board_id, position, title) VALUES (?, ?, ?, ?)",
                (column["id"], board_id, column_index, column["title"]),
            )
        for card_index, card in enumerate(default_board["cards"].values()):
            column_id = next(
                column["id"]
                for column in default_board["columns"]
                if card["id"] in column["cardIds"]
            )
            connection.execute(
                "INSERT INTO cards (id, board_id, column_id, title, details, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    card["id"],
                    board_id,
                    column_id,
                    card["title"],
                    card["details"],
                    card_index,
                    utc_now(),
                    utc_now(),
                ),
            )
        connection.commit()
        return board_id
    finally:
        connection.close()


def _serialize_board(user_id: str) -> dict:
    board_id = _ensure_board_for_user(user_id)
    connection = _connect_db()
    try:
        columns = connection.execute(
            "SELECT id, title, position FROM columns WHERE board_id = ? ORDER BY position ASC",
            (board_id,),
        ).fetchall()
        card_rows = connection.execute(
            "SELECT id, column_id, title, details, position FROM cards WHERE board_id = ? ORDER BY position ASC",
            (board_id,),
        ).fetchall()

        board_columns = []
        cards_by_id = {}
        for row in card_rows:
            cards_by_id[row["id"]] = {
                "id": row["id"],
                "title": row["title"],
                "details": row["details"],
            }

        for row in columns:
            card_ids = [
                card_row["id"]
                for card_row in card_rows
                if card_row["column_id"] == row["id"]
            ]
            board_columns.append({
                "id": row["id"],
                "title": row["title"],
                "cardIds": card_ids,
            })

        return {"columns": board_columns, "cards": cards_by_id}
    finally:
        connection.close()


def _replace_board_for_user(username: str, payload: dict) -> dict:
    user_id = _get_user_id(username)
    board_id = _ensure_board_for_user(user_id)
    connection = _connect_db()
    try:
        connection.execute("DELETE FROM cards WHERE board_id = ?", (board_id,))
        connection.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

        for position, column in enumerate(payload.get("columns", [])):
            column_id = column.get("id") or f"column-{position}-{board_id}"
            connection.execute(
                "INSERT INTO columns (id, board_id, position, title) VALUES (?, ?, ?, ?)",
                (column_id, board_id, position, column.get("title", f"Column {position + 1}")),
            )

        for position, card in enumerate(payload.get("cards", {}).values()):
            card_id = card.get("id") or f"card-{position}-{board_id}"
            column_id = next(
                (column.get("id") for column in payload.get("columns", []) if card_id in column.get("cardIds", [])),
                None,
            )
            if column_id is None:
                continue
            connection.execute(
                "INSERT INTO cards (id, board_id, column_id, title, details, position, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    card_id,
                    board_id,
                    column_id,
                    card.get("title", "Untitled card"),
                    card.get("details", ""),
                    position,
                    utc_now(),
                    utc_now(),
                ),
            )

        connection.execute(
            "UPDATE boards SET updated_at = ? WHERE id = ?",
            (utc_now(), board_id),
        )
        connection.commit()
        return _serialize_board(user_id)
    finally:
        connection.close()


def call_openrouter(prompt: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    response = httpx.post(
        OPENROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "PM MVP",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 200,
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json()
    message = payload["choices"][0]["message"]["content"]
    if isinstance(message, list):
        return "".join(part.get("text", "") for part in message)
    return str(message)


def serve_frontend_index() -> FileResponse:
    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return FileResponse(FALLBACK_STATIC_DIR / "index.html")


if (FRONTEND_DIST_DIR / "_next").exists():
    app.mount("/_next", StaticFiles(directory=FRONTEND_DIST_DIR / "_next"), name="next_static")


app = app


@app.get("/")
async def read_root() -> FileResponse:
    return serve_frontend_index()


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "pm-backend"}


@app.get("/api/hello")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello from PM backend"}


@app.post("/api/ai/test")
async def ai_test(payload: dict | None = Body(default=None)) -> dict[str, str]:
    prompt = "2+2"
    if payload and isinstance(payload, dict):
        prompt = str(payload.get("prompt", prompt))

    try:
        response = call_openrouter(prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"OpenRouter request failed: {exc}") from exc

    return {"prompt": prompt, "response": response}


@app.get("/api/users/{username}/board")
async def get_board(username: str) -> dict:
    user_id = _get_user_id(username)
    return _serialize_board(user_id)


@app.put("/api/users/{username}/board")
async def update_board(username: str, payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Board payload must be an object.")
    if "columns" not in payload or "cards" not in payload:
        raise HTTPException(status_code=400, detail="Board payload must include columns and cards.")
    return _replace_board_for_user(username, payload)


@app.get("/{path:path}")
async def catch_all(path: str) -> FileResponse:
    if path.startswith("api"):
        raise HTTPException(status_code=404)

    requested_path = FRONTEND_DIST_DIR / path
    if requested_path.is_file():
        return FileResponse(requested_path)

    return serve_frontend_index()


init_db()
