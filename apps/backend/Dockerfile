FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory to the monorepo root
WORKDIR /app

# 1. Copy only the dependency manifests first for maximum layer caching
COPY pyproject.toml uv.lock ./
COPY apps/backend/pyproject.toml ./apps/backend/
COPY apps/agents/pyproject.toml ./apps/agents/
COPY apps/realtime-worker/pyproject.toml ./apps/realtime-worker/

# 2. Install dependencies (this layer caches globally unless dependencies change)
RUN uv sync --frozen --no-install-project --no-dev

# 3. Copy the actual source code for this specific app
COPY apps/backend ./apps/backend

# 4. Final sync to install the project itself (very fast, just links the source)
RUN uv sync --frozen --no-dev --package backend

# Set the working directory to the specific app
WORKDIR /app/apps/backend

# Expose the backend port
EXPOSE 8000

# Run the FastAPI server
CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
