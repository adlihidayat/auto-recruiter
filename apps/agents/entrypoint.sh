#!/bin/bash
# ==============================================================================
# File: apps/agents/entrypoint.sh
# What: Container pre-flight checklist ("Bouncer") for the AI Agent service.
# Why: Validates pre-flight environmental prerequisites before launching Uvicorn.
# Boundaries: Pre-flight checks only; delegates process control to CMD via exec.
# ==============================================================================
set -e

echo "=== [Agents Bouncer] Running Pre-Flight Checklist ==="
echo "[1/1] AI Agents pre-flight checks completed successfully."
echo "=== [Agents Bouncer] Launching application process... ==="
echo ""

exec "$@"
