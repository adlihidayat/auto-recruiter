"""
What: Custom LLM bridge for LiveKit's VoicePipelineAgent.
Why: Invokes the LangGraph interviewer-agent in-process and integrates it with LiveKit.
Boundaries: Connects LiveKit ChatContext to LangGraph InterviewerState.
"""

import asyncio
import logging
import importlib
from typing import AsyncIterable, Any

from livekit.agents import llm
from src.worker.session.interview_session import InterviewSessionState
from src.worker.core.backend_client import BackendClient
from src.worker.session.schemas import FinishGoalPayload, TranscriptTurn

interviewer_graph_module = importlib.import_module("interviewer-agent.graph")
interviewer_graph = interviewer_graph_module.graph

logger = logging.getLogger("worker.turn_handler")

class InterviewerLLMStream(llm.LLMStream):
    def __init__(self, message_to_candidate: str):
        super().__init__(None, None)
        self._message = message_to_candidate
        self._yielded = False

    async def __anext__(self):
        if self._yielded:
            raise StopAsyncIteration
        
        self._yielded = True
        return llm.ChatChunk(
            choices=[
                llm.Choice(
                    delta=llm.ChoiceDelta(content=self._message, role="assistant"),
                    index=0
                )
            ]
        )
    
    async def aclose(self):
        pass

class InterviewerLLM(llm.LLM):
    def __init__(self, session_state: InterviewSessionState, backend_client: BackendClient, shutdown_callback=None):
        super().__init__()
        self.session_state = session_state
        self.backend_client = backend_client
        self.shutdown_callback = shutdown_callback

    def chat(self, chat_ctx: llm.ChatContext, **kwargs) -> llm.LLMStream:
        """
        Called by VoicePipelineAgent when a new turn starts (after candidate finishes speaking).
        """
        # Find the latest user message
        user_msg = None
        for msg in reversed(chat_ctx.messages()):
            if msg.role == "user":
                if isinstance(msg.content, str):
                    user_msg = msg.content
                    break
                elif isinstance(msg.content, list):
                    # In LiveKit >= 1.8, content is a list of ChatContent
                    text_parts = []
                    for c in msg.content:
                        # try to get .text or .content
                        if hasattr(c, "text") and c.text:
                            text_parts.append(c.text)
                        elif isinstance(c, str):
                            text_parts.append(c)
                    user_msg = " ".join(text_parts)
                    break

        transcript = user_msg or ""
        logger.info(f"Received candidate transcript: {transcript}")
        
        # We need to return an LLMStream synchronously, so we start a task to run the graph
        # and yield chunks from it.
        # But wait, VoicePipelineAgent expects the LLMStream to yield chunks asynchronously.
        # So we can do the graph execution inside the stream's __anext__.
        
        conn_opts = kwargs.get("conn_options")
        # In newer LiveKit versions, APIConnectOptions might be required, we can pass it if it's there
        stream = GraphExecutionStream(
            llm_instance=self,
            chat_ctx=chat_ctx,
            conn_options=conn_opts,
            session_state=self.session_state,
            backend_client=self.backend_client,
            transcript=transcript,
            shutdown_callback=self.shutdown_callback
        )
        return stream

class GraphExecutionStream(llm.LLMStream):
    def __init__(self, llm_instance: llm.LLM, chat_ctx: llm.ChatContext, conn_options: Any, session_state: InterviewSessionState, backend_client: BackendClient, transcript: str, shutdown_callback=None):
        super().__init__(
            llm=llm_instance,
            chat_ctx=chat_ctx,
            tools=[],
            conn_options=conn_options
        )
        self.session_state = session_state
        self.backend_client = backend_client
        self.transcript = transcript
        self.shutdown_callback = shutdown_callback

    async def _execute_graph(self) -> str:
        # Check if interview is finished
        if self.session_state.current_goal is None:
            logger.info("All goals completed. Concluding interview.")
            if self.shutdown_callback:
                asyncio.create_task(self.shutdown_callback())
            return "Thank you for your time, the interview is now concluded. Have a great day!"
            
        # 1. Update session state with candidate transcript
        self.session_state.add_history_item(role="candidate", content=self.transcript)
        
        # 2. Prepare LangGraph input
        input_state = self.session_state.get_agent_input_state(self.transcript)
        
        # 3. Invoke LangGraph
        try:
            logger.info("Invoking LangGraph interviewer-agent...")
            result_state = await interviewer_graph.ainvoke(input_state)
            decision = result_state.get("decision")
            
            if not decision:
                return "I'm sorry, I encountered an internal error. Let's try that again."
                
            action = decision.action
            message = decision.message_to_candidate
            
            # 4. Update session state with interviewer's response
            self.session_state.add_history_item(role="interviewer", content=message)
            
            # 5. Handle Advance
            if action == "advance":
                logger.info("Agent decided to advance. Saving goal and moving to next.")
                # We hit the backend /finish endpoint
                payload = FinishGoalPayload(transcripts=[])
                for turn in self.session_state.goal_history:
                    payload.transcripts.append(TranscriptTurn(
                        goal_id=self.session_state.current_goal.goal_id,
                        role=turn.role,
                        content=turn.content,
                        action=action if turn.role == "interviewer" else None,
                        reasoning=decision.reasoning if turn.role == "interviewer" else None
                    ))
                
                # TEMPORARILY DISABLED TO PREVENT 422 ERRORS FROM STUB GOALS
                # Fire and forget the backend call to avoid blocking speech
                # asyncio.create_task(self.backend_client.finish_goal(self.session_state.candidate_id, payload))
                
                # Advance local state
                self.session_state.advance_goal()
                
            return message
            
        except Exception as e:
            logger.error(f"Error during graph execution: {e}", exc_info=True)
            return f"I apologize, but I encountered an internal python error: {e}"

    async def _run(self) -> None:
        try:
            message = await self._execute_graph()
            chunk = llm.ChatChunk(
                id="msg",
                delta=llm.ChoiceDelta(content=message, role="assistant")
            )
            self._event_ch.send_nowait(chunk)
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            chunk = llm.ChatChunk(
                id="err",
                delta=llm.ChoiceDelta(content="I'm sorry, I encountered an internal error.", role="assistant")
            )
            self._event_ch.send_nowait(chunk)
