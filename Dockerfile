FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/app ./app
COPY backend/pyproject.toml ./pyproject.toml

RUN uv pip install --system --no-cache-dir "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" "pytest>=8.3.0" "httpx>=0.28.0" "python-dotenv>=1.0.1"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
