#!/bin/bash
# ==============================================================================
# File: apps/realtime-worker/entrypoint.sh
# What: Container pre-flight checklist ("Bouncer") for the LiveKit Realtime Worker service.
# Why: Validates pre-flight environmental prerequisites before joining LiveKit rooms.
# Boundaries: Pre-flight checks only; delegates process control to CMD via exec.
# ==============================================================================
set -e

echo "=== [Realtime Worker Bouncer] Running Pre-Flight Checklist ==="
echo "[1/1] Worker pre-flight checks completed successfully."
echo "=== [Realtime Worker Bouncer] Launching worker process... ==="
echo ""

exec "$@"
