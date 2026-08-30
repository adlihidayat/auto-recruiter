"""
What: Entry point for the livekit-agents worker.
Why: Registers the worker to listen for new rooms and handles job dispatching.
Boundaries: Contains only worker initialization and job acceptance logic. Complex turn handling is delegated.
"""

import os
import sys
import logging
import asyncio

# Ensure root directory and apps/agents are in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
AGENTS_DIR = os.path.join(ROOT_DIR, "apps/agents")
for p in [ROOT_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)
from livekit import api
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    JobRequest,
    WorkerOptions,
    cli,
    voice,
)
from livekit.plugins import silero, deepgram

from dotenv import load_dotenv

# Load .env file from worker directory
worker_env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(worker_env_path)

from src.worker.core.config import settings
from src.worker.core.backend_client import BackendClient
from src.worker.session.interview_session import InterviewSessionState
from src.worker.session.turn_handler import InterviewerLLM

logger = logging.getLogger("worker")
backend_client = BackendClient()

def prewarm(proc: JobProcess):
    """
    Preloads necessary models before the worker accepts jobs.
    """
    proc.userdata["vad"] = silero.VAD.load(
        activation_threshold=0.8,
        min_speech_duration=0.2,
        min_silence_duration=1.0,
    )

async def entrypoint(ctx: JobContext):
    """
    Called when the worker successfully joins a room.
    The room name matches the candidate's UUID.
    """
    candidate_id = ctx.room.name
    logger.info(f"Connecting to room: {candidate_id}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize state.
    import importlib
    interviewer_state = importlib.import_module("interviewer-agent.state")
    Goal = interviewer_state.Goal
    
    stub_goal_1 = Goal(
        goal_id="g_01",
        goal="Evaluate the candidate's ability to independently handle complex POS scenarios, including processing returns, applying multiple discounts, and resolving common register errors while maintaining accuracy.",
        topic="POS Transaction Management",
        suggested_opening="Imagine a customer comes to your register wanting to return an item without a receipt, but the item is currently showing as 'out of stock' in our system despite being on the shelf. Walk me through how you would handle this transaction while ensuring our inventory and reporting remain accurate.",
        passing_criteria=["Prioritizes verifying the item via SKU/serial number scan to ensure accurate identification", "Mentions checking for alternative proof of purchase like loyalty account or email lookup before proceeding", "Identifies the need to follow company policy for non-receipted returns, such as issuing store credit rather than cash", "Acknowledges the inventory mismatch and suggests flagging the item for a manual stock count or system sync check", "States that manager approval or specific user permissions are required for non-receipted or high-value returns"],
        pushback_triggers=[],
        wrong_answer_signals=["Suggests processing the return as a cash refund without any proof of purchase or manager oversight", "Ignores the inventory discrepancy entirely, failing to mention the need to reconcile the physical stock with the system", "Claims that POS errors like inventory mismatches should always be escalated to IT support immediately without attempting basic verification", "Suggests overriding system rules or bypassing the return workflow to 'make the customer happy' without documentation"],
        interview_time_in_minute=1
    )
    
    stub_goal_2 = Goal(
        goal_id="g_02",
        goal="Evaluate the candidate's approach to prioritizing floor maintenance tasks (restocking, folding, signage) during high-traffic periods to ensure store standards are met without neglecting customer assistance.",
        topic="Operational Efficiency and Merchandising",
        suggested_opening="It is a busy Saturday afternoon, the store is crowded, and you notice the fitting rooms are messy, a display table needs folding, and there is a line forming at the register. How do you decide which task to prioritize while ensuring customers still receive help?",
        passing_criteria=["Prioritizes customer-facing interactions and safety over non-urgent maintenance tasks", "Mentions delegating tasks to other team members if available", "Identifies the need to balance zone maintenance with active selling", "Suggests performing maintenance tasks in short bursts or micro-tasks rather than deep cleaning during peak hours"],
        pushback_triggers=[],
        wrong_answer_signals=["Suggests ignoring customers to finish folding or restocking tasks", "Claims that store appearance is more important than customer service during peak traffic", "States that all tasks must be completed perfectly before assisting the next customer"],
        interview_time_in_minute=1
    )

    session_state = InterviewSessionState(candidate_id=candidate_id, goals=[stub_goal_1, stub_goal_2])
    
    async def shutdown_callback():
        logger.info("Scheduling room disconnect in 5 seconds...")
        await asyncio.sleep(5)
        logger.info("Disconnecting room now.")
        try:
            livekit_api = api.LiveKitAPI(settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret)
            await livekit_api.room.delete_room(api.DeleteRoomRequest(room=ctx.room.name))
            await livekit_api.aclose()
        except Exception as e:
            logger.error(f"Failed to delete room: {e}")
        
    interviewer_llm = InterviewerLLM(
        session_state=session_state, 
        backend_client=backend_client,
        shutdown_callback=shutdown_callback
    )

    session = voice.AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        tts=deepgram.TTS(),
        llm=interviewer_llm,
    )
    
    agent = voice.Agent(instructions="You are an automated technical interviewer.")
    await session.start(agent, room=ctx.room)
    logger.info("Voice pipeline session started.")
    
    # Speak the first goal's opening
    if session_state.current_goal:
        greeting = f"Welcome to the interview! {session_state.current_goal.suggested_opening}"
        session_state.add_history_item(role="interviewer", content=greeting)
        await session.say(greeting, allow_interruptions=True)

    # Keep entrypoint alive until room disconnects or candidate leaves
    disconnected_event = asyncio.Event()

    @ctx.room.on("disconnected")
    def _on_disconnected(*args):
        logger.info("Room disconnected. Ending session.")
        disconnected_event.set()

    await disconnected_event.wait()

async def request_fnc(req: JobRequest) -> None:
    """
    Called when a new room is created on the LiveKit server.
    We automatically accept all incoming jobs assuming room.name == candidate_id.
    """
    logger.info(f"Received job request for room {req.room.name}. Accepting...")
    await req.accept()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            agent_name="interviewer-agent",
            entrypoint_fnc=entrypoint,
            request_fnc=request_fnc,
            prewarm_fnc=prewarm,
            ws_url=settings.livekit_url,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )
    )
