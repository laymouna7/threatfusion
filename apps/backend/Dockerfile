FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY apps/backend/pyproject.toml apps/backend/uv.lock* ./

RUN uv sync --frozen --no-dev --no-install-project

COPY apps/backend/ ./

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
