# Realtime Worker Tests Manifest (`apps/realtime-worker/tests`)

## Purpose
Integration and unit testing scripts for validating room connection, participant events, and agent graph execution.

## File Mapping

| File Name | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `test_client.py` | Integration test for connecting to LiveKit room via Python RTC SDK | `livekit.rtc`, `livekit.api` |
| `test_graph.py` | Standalone graph execution test for `interviewer-agent` | `interviewer-agent.graph` |
| `mocks/mock_frontend.html` | Standalone HTML client for testing agent voice audio without frontend server | LiveKit Client JS SDK |
