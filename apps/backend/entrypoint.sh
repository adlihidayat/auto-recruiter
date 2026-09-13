#!/bin/bash
# ==============================================================================
# File: apps/backend/entrypoint.sh
# What: Container pre-flight checklist ("Bouncer") for the FastAPI backend service.
# Why: Ensures mandatory prep work (like Alembic database migrations) completes
#      before the Uvicorn application server starts.
# Boundaries: Handles pre-flight checks only; delegates process control to CMD via exec.
# ==============================================================================
set -e

echo "=== [Backend Bouncer] Running Pre-Flight Checklist ==="

# Step 1: Execute database migrations
echo "[1/2] Executing database migrations (Alembic)..."
uv run alembic upgrade head

echo "[2/2] Pre-flight checklist completed successfully."
echo "=== [Backend Bouncer] Launching application process... ==="
echo ""

# Hand off execution to the CMD defined in Dockerfile or Compose (replaces PID 1)
exec "$@"
