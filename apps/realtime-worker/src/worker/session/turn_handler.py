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

def _is_continuation(prev_candidate_content: str, new_transcript: str) -> bool:
    """
    Returns True if `new_transcript` is a continuation of `prev_candidate_content`,
    indicating that the earlier VAD trigger was premature (noisy).

    Why: Deepgram sometimes fires a final transcript event mid-sentence when there is a
    brief pause. The candidate then continues speaking, producing a longer transcript.
    We detect this by checking that the previous (shorter) partial text is contained
    within the new (longer) text. We normalise both strings to lower-case and strip
    punctuation before comparing to handle minor STT transcription differences.
    """
    if not prev_candidate_content or not new_transcript:
        return False
    
    # Only consider it a continuation if the new transcript is meaningfully longer.
    # A ratio of 1.3x or more suggests the candidate kept talking.
    if len(new_transcript) < len(prev_candidate_content) * 1.3:
        return False

    # Normalize: lowercase + strip common punctuation so minor STT differences don't block the match
    def _normalize(text: str) -> str:
        import re
        return re.sub(r"[.,!?;:'\"-]", "", text.lower()).strip()

    return _normalize(prev_candidate_content) in _normalize(new_transcript)

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
        logger.info(f"\n========================================\n[VAD] Candidate finished speaking. Received transcript: '{transcript}'\n========================================")
        
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
            logger.info("\n========================================\n[FLOW] All goals completed. Concluding interview.\n========================================")
            if self.shutdown_callback:
                asyncio.create_task(self.shutdown_callback())
            return "Thank you for your time, the interview is now concluded. Have a great day!"
            
        # 1. Update session state with candidate transcript.
        # Three cases to handle cleanly:
        #
        # Case A: Last item is a candidate turn — the previous LLM call was cancelled before it
        #   could respond. Simply overwrite the partial transcript with the newer, longer one.
        #
        # Case B: Last two items are [candidate(partial), interviewer(continuation prompt)] —
        #   the VAD fired prematurely, the agent responded asking the candidate to continue,
        #   and now we have the full continuation. This is the "noisy call" pattern the user
        #   described. We detect it by checking if the old partial is a prefix of the new full
        #   transcript. If so, REMOVE the noisy pair and replace with just the final full turn.
        #
        # Case C: Normal new turn — just append.
        history = self.session_state.goal_history
        if history and history[-1].role == "candidate":
            # Case A: overwrite the cancelled partial
            history[-1].content = self.transcript
        elif (
            len(history) >= 2
            and history[-1].role == "interviewer"
            and history[-2].role == "candidate"
            and _is_continuation(history[-2].content, self.transcript)
        ):
            # Case B: noisy VAD trigger — remove the (partial candidate + continuation prompt) pair
            history.pop()  # remove the interviewer continuation prompt
            history.pop()  # remove the partial candidate turn
            logger.info("[DEDUP] Removed noisy partial transcript pair. Replacing with final full turn.")
            self.session_state.add_history_item(role="candidate", content=self.transcript)
        else:
            # Case C: genuine new candidate turn
            self.session_state.add_history_item(role="candidate", content=self.transcript)
        
        # 2. Prepare LangGraph input
        input_state = self.session_state.get_agent_input_state(self.transcript)
        
        # 3. Invoke LangGraph
        try:
            logger.info("\n========================================\n[AGENT] Processing candidate's response through LangGraph...\n========================================")
            result_state = await interviewer_graph.ainvoke(input_state)
            decision = result_state.get("decision")
            
            if not decision:
                logger.error("[AGENT] Error: No decision returned by LangGraph!")
                return "I'm sorry, I encountered an internal error. Let's try that again."
                
            action = decision.action
            message = decision.message_to_candidate
            
            reasoning_text = getattr(decision, "reasoning", "")
            logger.info(f"\n========================================\n[AGENT] Decision reached:\nAction: {action.upper()}\nMessage: '{message}'\n========================================")
            
            # 5. Handle Advance vs Pushback
            if action == "advance":
                is_final_goal = (self.session_state.current_goal_index + 1 >= len(self.session_state.goals))
                
                if is_final_goal:
                    # Final goal: append closing message to current goal's history before saving
                    self.session_state.add_history_item(role="interviewer", content=message)
                    history_to_save = list(history)
                else:
                    # Non-final goal: Goal's history to save is history BEFORE adding transition message
                    history_to_save = list(history)

                goal_ref = self.session_state.current_goal.goal_id
                candidate_id = self.session_state.candidate_id
                logger.info(f"\n========================================\n[DB] Saving transcripts for completed goal: {goal_ref}\n========================================")
                
                # Build the final, deduplicated transcript list for this goal.
                transcripts = [
                    {
                        "role": turn.role,
                        "content": turn.content,
                        # Stamp action/reasoning on the final turn of this goal's saved history
                        "action": (action if turn == history_to_save[-1] else None),
                        "reasoning": (reasoning_text if turn == history_to_save[-1] else None),
                        "trigger_matched": getattr(decision, "trigger_matched", None),
                        "flag_for_human_review": getattr(decision, "flag_for_human_review", False)
                    }
                    for turn in history_to_save
                ]
                
                # Fire-and-forget with explicit error logging so failures are visible
                async def _save_transcripts(g_ref=goal_ref, t_list=transcripts):
                    try:
                        await self.backend_client.save_goal_transcripts(
                            candidate_id=candidate_id,
                            goal_ref=g_ref,
                            transcripts=t_list
                        )
                        logger.info(f"[DB] Transcripts saved for goal {g_ref}.")
                    except Exception as exc:
                        logger.error(f"[DB] Failed to save transcripts for goal {g_ref}: {exc}", exc_info=True)
                
                asyncio.create_task(_save_transcripts())
                
                # Advance local state
                self.session_state.advance_goal()
                remaining = len(self.session_state.goals) - self.session_state.current_goal_index
                logger.info(f"[FLOW] Advanced to next goal. Remaining goals: {remaining}")
                
                if not is_final_goal:
                    # Non-final goal: the transition message ("Moving on to our next topic...")
                    # becomes the opening interviewer turn for the NEW goal!
                    self.session_state.add_history_item(role="interviewer", content=message)
                else:
                    logger.info("\n========================================\n[FLOW] All goals completed. Scheduling interview conclusion.\n========================================")
                    
                    # Fire-and-forget finish_interview with explicit error logging
                    async def _finish_interview():
                        try:
                            logger.info(f"[DB] Calling finish_interview for candidate {candidate_id}...")
                            await self.backend_client.finish_interview(candidate_id)
                            logger.info(f"[DB] finish_interview succeeded. Grading agent dispatched.")
                        except Exception as exc:
                            logger.error(f"[DB] finish_interview FAILED for candidate {candidate_id}: {exc}", exc_info=True)
                    
                    asyncio.create_task(_finish_interview())
                    
                    if self.shutdown_callback:
                        # Schedule room deletion after a short delay to allow TTS to finish
                        asyncio.create_task(self.shutdown_callback())
            else:
                # Pushback: add interviewer response to current goal's history
                self.session_state.add_history_item(role="interviewer", content=message)
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
