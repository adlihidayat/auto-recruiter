"""
What: Synchronous / Asynchronous node for running StackOne Defender against candidate transcripts.
Why: Prevents prompt injection attacks from reaching the LLM, saving tokens and preserving safety boundaries.
Boundaries: Does not contain LLM calls, just local ONNX evaluation. Short circuits the graph if injection is detected.
"""

import logging

try:
    from stackone_defender import create_prompt_defense
    from stackone_defender.types import MultiheadConfig
except ImportError:
    create_prompt_defense = None
    MultiheadConfig = None

from ..state import InterviewerState, InterviewerDecision

logger = logging.getLogger("agent.interviewer.injection")

# Initialize StackOne Defender ONNX model once
if create_prompt_defense and MultiheadConfig:
    defender = create_prompt_defense(
        tier2_config={'multihead': MultiheadConfig(main_threshold=0.8, aux_threshold=0.5)}
    )
    # Disable Tier-1 pattern removal, allowing only normalizations, relying on Tier-2 ML
    if hasattr(defender, '_tool_sanitizer') and hasattr(defender._tool_sanitizer, '_pattern_detector'):
        defender._tool_sanitizer._pattern_detector._patterns = []
else:
    defender = None


async def checkPromptInjection(state: InterviewerState) -> dict:
    """
    Evaluates the latest transcript for injection patterns. 
    If detected, returns a short-circuit decision state.
    """
    transcript = state.get("latest_candidate_transcript", "")
    
    if not defender or not transcript:
        return {}
        
    try:
        defense_result = await defender.defend_tool_result_async(value=transcript, tool_name="transcribe")
        
        if defense_result.risk_level == "high":
            logger.warning(f"[SECURITY] Injection Detected by Agent! Risk Level: HIGH")
            
            # Create a hardcoded decision to end the interview
            decision = InterviewerDecision(
                scratchpad="SECURITY_INTERCEPT: Prompt injection or malicious intent detected in candidate transcript. Bypassing standard evaluation and immediately terminating the interview to prevent exploitation.",
                action="end_interview",
                message_to_candidate="we suspect a malicious behavior. We will conclude the interview now. Thank you for your time.",
                progression_override=False,
                flag_for_human_review=True
            )
            
            return {"decision": decision}
            
    except Exception as e:
        logger.error(f"[SECURITY] Defender check failed: {e}", exc_info=True)
        # Fail-open if the defender crashes, rather than dropping the call.
        
    return {}
