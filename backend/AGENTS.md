# Backend agent guide

## Purpose

This directory contains the FastAPI backend for the PM MVP. It is responsible for serving the local app shell, exposing health and API routes, and later handling the Kanban data model, persistence, and AI orchestration.

## Current state

The backend is in the initial scaffolding phase. It currently provides a minimal FastAPI service with a root page and a couple of simple API endpoints to prove the local stack is working.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLite is planned for the persistence layer
- uv is the preferred package manager for the Python environment in Docker and local setup

## Structure

- `app/main.py`: FastAPI app entry point with routes.
- `app/static/index.html`: minimal static HTML page that renders a "Hello World" message and fetches the health endpoint.
- `tests/test_main.py`: smoke tests for the root page and API routes.
- `pyproject.toml`: Python project metadata and dependencies.

## Expected behavior

The backend should:

- serve a simple root page for local validation;
- return a health status from `/api/health`;
- return a simple hello response from `/api/hello`;
- later expand to persist board state and integrate the AI backend.

## Local validation

Run from the project root or backend directory:

```bash
cd backend
uv sync
uv run pytest
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Notes

Keep the backend simple and closely aligned with the MVP requirements. Do not add heavy abstractions or extra features before the project is fully scaffolded and the requirements are signed off.