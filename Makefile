.PHONY: frontend realtime-worker backend-main agents

frontend:
	cd apps/frontend && npm run dev

realtime-worker:
	docker compose -f docker-compose.dev.yml up -d

backend-main:
	cd apps/backend && uv run --env-file ../../.env uvicorn app.main:app --app-dir src --port 8000 --reload

agents:
	cd apps/agents && uv run --env-file ../../.env uvicorn main:app --port 8001 --reload
