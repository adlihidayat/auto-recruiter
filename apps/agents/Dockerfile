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
COPY apps/agents ./apps/agents

# 4. Final sync to install the project itself
RUN uv sync --frozen --no-dev --package agents

# 5. Pre-download the ONNX injection model (bakes it into the image)
ENV ONNX_INJECTION_MODEL_DIR=/app/assets/onnx_model
RUN uv run python packages/core-ai-lib/scripts/download_model.py

# Set the working directory to the specific app
WORKDIR /app/apps/agents

# Ensure entrypoint script is executable
RUN chmod +x ./entrypoint.sh

# Expose the agents port
EXPOSE 8001

# Set entrypoint and CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

