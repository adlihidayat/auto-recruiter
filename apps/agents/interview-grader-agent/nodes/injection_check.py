"""
What: Placeholder node for detecting prompt injection in candidate transcripts.
Why: Part of Phase 1 parallel execution. Runs over every candidate turn.
Boundaries: Currently a stub. Does not modify core analysis or communication logic.
"""
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel
from langsmith import traceable
from ..state import GraderState, InjectionFinding
from apps.agents.shared.clients import get_prompt_guard_score, gemini_flash_lite
from ..prompts.injection_prompt import INJECTION_PROMPT

HIGH_THRESHOLD = 0.9
LOW_THRESHOLD = 0.1

 
INJECTION_PATTERNS_INSTRUCTION_OVERRIDE = [
    r"(?i)ignore\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"(?i)disregard\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|prompts?)",
    r"(?i)forget\s+(all\s+|everything\s+)?(the\s+)?(previous|prior|above)\s*(instructions?)?",
    r"(?i)override\s+(the\s+)?(system|instructions?|rules?|rubric|scoring|criteria)",
    r"(?i)bypass\s+(the\s+)?(system|instructions?|rules?|filters?|guardrails?)",
    r"(?i)new\s+instructions?\s*:",
    r"(?i)from\s+now\s+on\s*,?\s*you\s+(will|must|should)",
    r"(?i)your\s+(new|real|true)\s+(task|instructions?|goal)\s+is",
]
 
INJECTION_PATTERNS_ROLE_MANIPULATION = [
    r"(?i)you\s+are\s+now\s+(a|an|in)\b",
    r"(?i)act\s+as\s+(if\s+you\s+are\s+|a\s+)?(a\s+different|an?\s+unrestricted)",
    r"(?i)pretend\s+(you\s+are|to\s+be)",
    r"(?i)developer\s+mode",
    r"(?i)jailbreak(ed)?",
    r"(?i)\bDAN\b",
    r"(?i)simulate\s+(a|an)\s+(unfiltered|unrestricted|jailbroken)",
]
 
INJECTION_PATTERNS_FAKE_MESSAGE_STRUCTURE = [
    r"(?i)^\s*\[?system\]?\s*:",
    r"(?i)^\s*\[?assistant\]?\s*:",
    r"(?i)<\s*/?system\s*>",
    r"(?i)<\s*/?im_start\s*>",
    r"(?i)###\s*(system|instruction)",
    r"(?i)end\s+of\s+(transcript|interview|conversation)\s*[.,]?\s*(system|new)",
]
 
INJECTION_PATTERNS_PROMPT_EXTRACTION = [
    r"(?i)(show|reveal|print|repeat|output)\s+(me\s+)?(the\s+)?(system\s+prompt|your\s+instructions?|the\s+rubric|the\s+grading\s+criteria)",
    r"(?i)what\s+(is|are)\s+your\s+(system\s+prompt|instructions?|rules?)",
    r"(?i)repeat\s+(the\s+)?(text|words?)\s+above",
]
 
INJECTION_PATTERNS_SCORE_MANIPULATION = [
    # Attacks specific to this system: trying to talk the grader into a
    # score/verdict directly rather than earning it through the answer.
    r"(?i)give\s+me\s+(a\s+)?(perfect\s+score|10\s*/\s*10|full\s+marks|a\s+10)",
    r"(?i)mark\s+(me|this)\s+as\s+(passed?|hired?|a\s+hire)",
    r"(?i)(the\s+)?interviewer\s+(already\s+)?(confirmed|approved|said)\s+(i\s+)?(passed|hired|got\s+a)",
    r"(?i)(recommend|rate)\s+me\s+(for\s+)?(the\s+)?(job|position|role|hire)",
    r"(?i)ignore\s+(the\s+)?(rubric|criteria|scoring\s+guide)",
    r"(?i)set\s+(the\s+)?(score|confidence)\s+to\s+\d",
]
 
INJECTION_REGEX_PATTERNS = (
    INJECTION_PATTERNS_INSTRUCTION_OVERRIDE
    + INJECTION_PATTERNS_ROLE_MANIPULATION
    + INJECTION_PATTERNS_FAKE_MESSAGE_STRUCTURE
    + INJECTION_PATTERNS_PROMPT_EXTRACTION
    + INJECTION_PATTERNS_SCORE_MANIPULATION
)

class Layer3Extraction(BaseModel):
    findings: List[InjectionFinding]

@traceable(name="run_injection_check")
def run_injection_check(state: GraderState) -> Dict[str, Any]:
    """
    Injection check node running 3 layers of defense.
    Layer 1: Regex
    Layer 2: HF PromptGuard API
    Layer 3: LLM Span Classifier (conditional)
    """
    findings: List[InjectionFinding] = []
    queued_turns = []
    
    # Iterate through all goals and candidate turns
    goals = state.get("goals", [])
    
    for goal in goals:
        goal_id = goal.goal_id if hasattr(goal, 'goal_id') else goal.get("goal_id")
        history = goal.interaction_history if hasattr(goal, 'interaction_history') else goal.get("interaction_history", [])
        
        for idx, turn in enumerate(history):
            role = turn.role if hasattr(turn, 'role') else turn.get("role")
            content = turn.content if hasattr(turn, 'content') else turn.get("content", "")
            
            if role != "candidate":
                continue
                
            turn_id = f"t_{idx:02d}" # Use a generated turn ID if missing upstream
            
            # Layer 1: Regex Check
            l1_hit = False
            l1_span = ""
            for pattern in INJECTION_REGEX_PATTERNS:
                match = re.search(pattern, content)
                if match:
                    l1_hit = True
                    l1_span = match.group(0)
                    break
                    
            # Layer 2: PromptGuard Score
            l2_score = get_prompt_guard_score(content)
            
            # Routing Decision
            if l1_hit and l2_score >= HIGH_THRESHOLD:
                # Confident Flag
                findings.append(InjectionFinding(
                    goal_id=goal_id,
                    turn_id=turn_id,
                    layer_detected="layer_1_regex | layer_2_classifier",
                    layer_2_score=l2_score,
                    confidence="high",
                    quote=l1_span,
                    rationale=f"Regex matched '{l1_span}' and PromptGuard scored {l2_score:.2f} (>= {HIGH_THRESHOLD})"
                ))
            elif not l1_hit and l2_score < LOW_THRESHOLD:
                # Confident Safe
                continue
            else:
                # Queue for Layer 3
                queued_turns.append({
                    "goal_id": goal_id,
                    "turn_id": turn_id,
                    "content": content,
                    "l1_hit": l1_hit,
                    "l1_span": l1_span,
                    "l2_score": l2_score
                })
                
    # Layer 3: Batched LLM call (if any queued turns)
    if queued_turns:
        try:
            # Format queued turns for the prompt
            turns_text = "\n---\n".join([
                f"Goal ID: {qt['goal_id']}\nTurn ID: {qt['turn_id']}\nL1 Hit: {qt['l1_hit']}\nL2 Score: {qt['l2_score']:.2f}\nCandidate Text: {qt['content']}" 
                for qt in queued_turns
            ])
            
            chain = INJECTION_PROMPT | gemini_flash_lite.with_structured_output(Layer3Extraction)
            result = chain.invoke({"queued_turns": turns_text})
            
            for f in result.findings:
                # Add metadata since the LLM might hallucinate it
                f.layer_detected = "layer_3_llm"
                findings.append(f)
                
        except Exception as e:
            print(f"Layer 3 LLM failed: {e}")
            # Fail closed as per GEMINI.md: surface them in findings with "uncertain"
            for qt in queued_turns:
                findings.append(InjectionFinding(
                    goal_id=qt["goal_id"],
                    turn_id=qt["turn_id"],
                    layer_detected="layer_3_llm_failed",
                    layer_2_score=qt["l2_score"],
                    confidence="uncertain",
                    quote=qt["l1_span"] if qt["l1_hit"] else qt["content"][:100],
                    rationale="Layer 3 LLM failed to process this queued turn."
                ))
                
    return {
        "injection_check": {
            "injection_findings": [f.model_dump() for f in findings]
        }
    }
