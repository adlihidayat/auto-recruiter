# Auto Recruiter

An autonomous AI pipeline that completely automates candidate screening through real-time voice interviews and dynamic grading.

## ✨ Features

- **Real-time AI Agents**: Instant response pipeline powered by ONNX injection detection and robust LLM routing.
- **Full-stack Monorepo**: Shared UI components for the frontend and shared core AI packages for the backend.
- **Containerized Infrastructure**: One-command boot for PostgreSQL, LiveKit, and all core services via Docker Compose.

## 🛠️ Tech Stack

| Category           | Technology                                        |
| :----------------- | :------------------------------------------------ |
| **Frontend**       | Next.js, React, Tailwind CSS                      |
| **Backend & AI**   | Python 3.12, FastAPI, uv, ONNX Runtime, LangGraph |
| **Infrastructure** | Docker, Docker Compose, PostgreSQL, LiveKit       |

## 📂 Repository Structure

```text
auto-recruiter/
├── apps/
│   ├── agents/            # AI Service (LangGraph, prompt templates, agent tools)
│   ├── backend/           # Core API (FastAPI, auth, database, business logic)
│   ├── frontend/          # Next.js Web App (UI, candidate reports)
│   └── realtime-worker/   # Python LiveKit Worker (Real-time WebRTC voice agent)
├── packages/
│   ├── core-ai-lib/       # Shared Python library (Schemas, AI clients, ONNX)
│   └── shared-ui/         # Shared React/TypeScript UI components
├── .env                   # Global environment variables
└── docker-compose.yml     # Production deployment configuration
```

## 🚀 Getting Started

To run Auto Recruiter locally, you just need a few mandatory API keys and Docker! The database and real-time voice server (LiveKit) are completely self-hosted and auto-configured out of the box.

### 1. Configure Environment Variables

Copy the provided template to create your `.env` file:

```bash
cp .env.example .env
```

Open your new `.env` file and fill in your mandatory API keys:

- `GEMINI_API_KEY1`
- `DEEPGRAM_API_KEY`
- `TAVILY_API_KEY`

_(Note: LangSmith tracing, HuggingFace models, LiveKit credentials, and PostgreSQL configurations are handled automatically or remain strictly optional)._

### 2. Boot the Infrastructure

Ensure you have Docker and Docker Compose installed. Then, spin everything up with:

```bash
docker compose up -d
```

> **⚠️ Note on First Build:** The initial `docker compose up` will take several minutes to complete. The system will automatically download large dependencies including PyTorch and the ONNX injection detection models (~500MB) during the build process. Subsequent boots will be nearly instantaneous.

### 3. Access the Application

Once the containers are healthy, open your browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
