"""
What: Entry point for the livekit-agents worker.
Why: Registers the worker to listen for new rooms and handles job dispatching.
Boundaries: Contains only worker initialization and job acceptance logic. Complex turn handling is delegated.
"""

import os
import sys
import logging
import asyncio
import warnings

warnings.filterwarnings("ignore")

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

# Suppress noisy third-party loggers for clean debugging
for log_name in ["google_genai", "google_genai.models", "google", "langsmith", "langsmith.client", "livekit", "livekit.agents", "livekit.plugins", "urllib3", "asyncio", "jwt"]:
    logging.getLogger(log_name).setLevel(logging.WARNING)

def prewarm(proc: JobProcess):
    """
    Preloads necessary models before the worker accepts jobs.
    """
    proc.userdata["vad"] = silero.VAD.load(
        activation_threshold=0.5,
        min_speech_duration=0.2,
        min_silence_duration=4.0,
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
    
    import json
    metadata = ctx.job.metadata
    goals = []
    
    if metadata:
        try:
            goals_data = json.loads(metadata)
            for g_data in goals_data:
                # The backend passes the goal_ref in 'goal_ref'. We map it to 'goal_id' for the agent's Goal schema.
                goals.append(
                    Goal(
                        goal_id=g_data.get("goal_ref", str(g_data.get("id"))),
                        goal=g_data.get("goal", ""),
                        topic=g_data.get("topic", ""),
                        suggested_opening=g_data.get("suggested_opening", ""),
                        passing_criteria=g_data.get("passing_criteria", []),
                        pushback_triggers=g_data.get("pushback_triggers", []),
                        wrong_answer_signals=g_data.get("wrong_answer_signals", []),
                        interview_time_in_minute=1 # Default or parsed from weight? Leaving as 1 for now.
                    )
                )
        except Exception as e:
            logger.error(f"Failed to parse goals from metadata: {e}")
            
    if not goals:
        # Fallback to a single generic goal if metadata is missing or fails to parse
        logger.warning("No goals found in metadata, falling back to generic stub goal.")
        goals = [
            Goal(
                goal_id="g_01",
                goal="Assess the candidate.",
                topic="General Assessment",
                suggested_opening="Welcome to the interview. Could you please introduce yourself?",
                passing_criteria=["Provides a clear introduction"],
                pushback_triggers=[],
                wrong_answer_signals=[],
                interview_time_in_minute=1
            )
        ]

    session_state = InterviewSessionState(candidate_id=candidate_id, goals=goals)
    
    async def shutdown_callback():
        # Wait for the agent to finish speaking the closing message before nuking the room.
        # `session` is resolved from the enclosing scope at call time — Python closures capture
        # the variable name, not its value, so this is safe even though `session` is assigned below.
        logger.info("Interview complete. Waiting for agent to finish speaking before closing room...")
        
        finished_speaking_event = asyncio.Event()
        
        def _on_agent_stopped_speaking(*args):
            finished_speaking_event.set()
        
        # Register once — fires as soon as TTS finishes the closing sentence
        session.on("agent_stopped_speaking", _on_agent_stopped_speaking)
        
        try:
            # 15-second hard timeout as a safety net in case the event never fires
            await asyncio.wait_for(finished_speaking_event.wait(), timeout=20.0)
            logger.info("Agent finished speaking. Closing room now.")
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for agent to finish speaking. Closing room anyway.")
        finally:
            session.off("agent_stopped_speaking", _on_agent_stopped_speaking)
        
        try:
            livekit_api = api.LiveKitAPI(settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret)
            await livekit_api.room.delete_room(api.DeleteRoomRequest(room=ctx.room.name))
            await livekit_api.aclose()
            logger.info("Room deleted successfully.")
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
        turn_handling={
            "turn_detection": "vad",
            "endpointing": {"min_delay": 3.0, "max_delay": 5.0},
            "interruption": {"enabled": False}
        }
    )
    
    agent = voice.Agent(instructions="You are an automated technical interviewer.")
    await session.start(agent, room=ctx.room)
    logger.info("Voice pipeline session started.")
    
    # Speak the first goal's opening
    if session_state.current_goal:
        greeting = f"Welcome to the interview! {session_state.current_goal.suggested_opening}"
        session_state.add_history_item(role="interviewer", content=greeting)
        await asyncio.sleep(1.5)
        await session.say(greeting)

    # Keep entrypoint alive until the room is closed (either by shutdown_callback or the candidate leaving).
    # IMPORTANT: Only shutdown_callback should delete the room. This handler just unblocks the wait.
    disconnected_event = asyncio.Event()

    @ctx.room.on("disconnected")
    def _on_disconnected(*args):
        logger.info("Room disconnected. Ending session.")
        disconnected_event.set()

    await disconnected_event.wait()
    logger.info("Entrypoint returning — room session complete.")

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
