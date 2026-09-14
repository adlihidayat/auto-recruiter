# Realtime Worker Scripts Manifest (`apps/realtime-worker/scripts`)

## Purpose
Helper utilities and developer scratch scripts for manual dispatch creation and isolated turn handler debugging.

## File Mapping

| File Name | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `create_dispatch.py` | Admin utility to register LiveKit room dispatch rules | `livekit.api` |
| `scratch.py` | Developer test script for testing turn handler and LLM stream locally | `InterviewSessionState`, `InterviewerLLM` |
