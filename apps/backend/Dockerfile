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
COPY packages/core-ai-lib/pyproject.toml ./packages/core-ai-lib/

# 2. Install dependencies (this layer caches globally unless dependencies change)
RUN uv sync --frozen --no-install-project --no-dev

# 3. Copy the actual source code for this specific app
COPY packages/core-ai-lib ./packages/core-ai-lib
COPY apps/backend ./apps/backend

# 4. Final sync to install the project itself (very fast, just links the source)
RUN uv sync --frozen --no-dev --package backend

# Set the working directory to the specific app
WORKDIR /app/apps/backend

# Ensure entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose the backend port
EXPOSE 8000

# Set entrypoint and CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]

