FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies that might be needed for audio/livekit C++ bindings
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

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

# 3. Copy the actual source code (worker requires agents in-process)
COPY packages/core-ai-lib ./packages/core-ai-lib
COPY apps/agents ./apps/agents
COPY apps/realtime-worker ./apps/realtime-worker

# 4. Final sync to install the project itself
RUN uv sync --frozen --no-dev --package realtime-worker

# Set the working directory to the specific app
WORKDIR /app/apps/realtime-worker

# Ensure entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Set entrypoint and CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "python", "-m", "src.worker.main", "start"]


