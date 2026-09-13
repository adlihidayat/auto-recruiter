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
COPY apps/agents ./apps/agents

# 4. Final sync to install the project itself
RUN uv sync --frozen --no-dev --package agents

# Set the working directory to the specific app
WORKDIR /app/apps/agents

# Ensure entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose the agents port
EXPOSE 8001

# Set entrypoint and CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8001"]

