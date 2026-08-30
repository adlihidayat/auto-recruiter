import asyncio
import os
import sys

# Setup paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AGENTS_DIR = os.path.join(ROOT_DIR, "apps/agents")
for p in [ROOT_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, "apps/agents/.env"))

import importlib
interviewer_state = importlib.import_module("interviewer-agent.state")
Goal = interviewer_state.Goal

from src.worker.session.interview_session import InterviewSessionState
from src.worker.session.turn_handler import InterviewerLLM
from src.worker.core.backend_client import BackendClient
from livekit.agents import llm

async def main():
    print("Testing Turn Handler...")
    
    # Stub goal
    stub_goal = Goal(
        goal_id="g_01",
        goal="Evaluate candidate understanding of the system.",
        topic="General",
        suggested_opening="Welcome to the interview! Let's start with a brief introduction.",
        passing_criteria=[],
        pushback_triggers=[],
        wrong_answer_signals=[],
        interview_time_in_minute=10
    )
    
    session_state = InterviewSessionState(candidate_id="test-candidate", goals=[stub_goal])
    backend_client = BackendClient()
    llm_bridge = InterviewerLLM(session_state=session_state, backend_client=backend_client)
    
    # Mock chat ctx
    chat_ctx = llm.ChatContext()
    chat_ctx.messages().append(llm.ChatMessage.create(text="Hi! My name is John.", role="user"))
    
    stream = llm_bridge.chat(chat_ctx)
    print("Stream initialized:", stream)
    
    async for chunk in stream:
        print("Chunk received:", chunk.choices[0].delta.content)
        
    print("Session state history length:", len(session_state.goal_history))
    
if __name__ == "__main__":
    asyncio.run(main())
