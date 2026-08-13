"""
What: Executes Call 2 (Communication) of the interview grader pipeline.
Why: Extracts evidence for communication traits (active listening, structure, etc.) using LLM, then grades them deterministically.
Boundaries: Conditionally executed; does not score technical correctness.
"""
import json
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from ..state import (
    GraderState, 
    CommunicationOutput, 
    CommunicationExtraction,
    CommunicationOutputData,
    CommOverallEval,
    CommTraitEval,
    CommEvidence
)
from apps.agents.shared.clients import gemini_flash_lite

COMMUNICATION_RUBRIC = {
    "active_listening": {
      "definition": "Candidate shows they actually processed what the interviewer said, instead of just waiting for their turn to talk.",
      "positive_signals": [
        {"id": "al_pos_reference_earlier", "desc": "Refers back to something interviewer said earlier"},
        {"id": "al_pos_clarifying_question", "desc": "Asks a clarifying question instead of guessing"},
        {"id": "al_pos_direct_answer", "desc": "Answer directly addresses the specific question asked"}
      ],
      "negative_signals": [
        {"id": "al_neg_ignores_question", "desc": "Answers a different question than the one asked"},
        {"id": "al_neg_repeats_self", "desc": "Repeats an earlier answer, ignoring the follow-up"},
        {"id": "al_neg_talks_over", "desc": "Interrupts or talks over the interviewer"}
      ]
    },
    "structure": {
      "definition": "Candidate organizes their answer in a logical order, instead of scattered thoughts.",
      "positive_signals": [
        {"id": "st_pos_clear_order", "desc": "Answer follows a clear order (steps, cause-then-effect)"},
        {"id": "st_pos_signpost", "desc": "Uses signposting like 'first...then...finally'"}
      ],
      "negative_signals": [
        {"id": "st_neg_scattered", "desc": "Jumps between unrelated points with no order"},
        {"id": "st_neg_no_conclusion", "desc": "Answer trails off with no clear ending"}
      ]
    },
    "assertiveness": {
      "definition": "Candidate commits to a position confidently, instead of hedging everything.",
      "positive_signals": [
        {"id": "as_pos_states_position", "desc": "Clearly states an opinion/recommendation"},
        {"id": "as_pos_defends_position", "desc": "When challenged, explains reasoning instead of caving immediately"}
      ],
      "negative_signals": [
        {"id": "as_neg_hedging", "desc": "Hedges so much no real position is ever given"},
        {"id": "as_neg_caves", "desc": "Abandons their answer the moment it's questioned, no pushback"}
      ]
    },
    "clarity": {
      "definition": "Candidate explains things so a listener can follow, without rambling or unexplained jargon.",
      "positive_signals": [
        {"id": "cl_pos_plain", "desc": "Explains a technical concept in plain terms, or defines jargon used"},
        {"id": "cl_pos_concise", "desc": "Gets to the point without unneeded repetition"}
      ],
      "negative_signals": [
        {"id": "cl_neg_jargon", "desc": "Uses technical terms with zero explanation"},
        {"id": "cl_neg_rambling", "desc": "Long-winded, repetitive, or hard to follow"}
      ]
    }
}

structured_llm_client = gemini_flash_lite.with_structured_output(CommunicationExtraction)

def trait_score(net_score: int, total_evidence: int) -> Optional[float]:
    """
    Computes a 0.0 - 10.0 continuous score for a communication trait based on net score.
    net_score = 0 sits at 5.0 (the old fail boundary), each net point shifts it by 1.
    """
    if total_evidence == 0:
        return None  # not addressed — excluded from aggregate
    return max(0.0, min(10.0, 5.0 + float(net_score)))

@traceable(name="run_communication")
def run_communication(state: GraderState) -> dict[str, Any]:
    """
    Call 2 - Communication.
    Step 1: LLM extracts communication signals based on rubric.
    Step 2: Deterministic code produces final grades.
    """
    print("Running communication analysis extraction...")

    from ..prompts.communication_prompt import (
        COMMUNICATION_SYSTEM_PROMPT,
        COMMUNICATION_USER_PROMPT,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", COMMUNICATION_SYSTEM_PROMPT),
        ("user", COMMUNICATION_USER_PROMPT),
    ])

    chain = prompt | structured_llm_client

    job_obj = state.get("job")
    job_name = job_obj.job_name if hasattr(job_obj, "job_name") else job_obj.get("job_name", "") if isinstance(job_obj, dict) else ""
    job_desc = job_obj.job_description if hasattr(job_obj, "job_description") else job_obj.get("job_description", "") if isinstance(job_obj, dict) else ""

    plan_meta_obj = state.get("plan_meta")
    difficulty = plan_meta_obj.difficulty if hasattr(plan_meta_obj, "difficulty") else plan_meta_obj.get("difficulty", "") if isinstance(plan_meta_obj, dict) else ""
    comm_weight = plan_meta_obj.communication_weight if hasattr(plan_meta_obj, "communication_weight") else plan_meta_obj.get("communication_weight", "") if isinstance(plan_meta_obj, dict) else ""

    job_context = f"Role: {job_name}\nDescription: {job_desc}"
    plan_meta_str = f"Difficulty: {difficulty}\nCommunication Weight: {comm_weight}"

    # Build concatenated transcript list of dicts for LLM
    transcript_list = []
    goals = state.get("goals", [])
    for g in goals:
        history = g.interaction_history if hasattr(g, "interaction_history") else g.get("interaction_history", [])
        for t in history:
            turn_id = t.turn_id if hasattr(t, "turn_id") else t.get("turn_id", "")
            role = t.role if hasattr(t, "role") else t.get("role", "")
            content = t.content if hasattr(t, "content") else t.get("content", "")
            transcript_list.append({
                "turn_id": turn_id,
                "role": role,
                "content": content
            })
            
    transcript_json = json.dumps(transcript_list, indent=2)
    rubric_json = json.dumps(COMMUNICATION_RUBRIC, indent=2)

    # Step 1: LLM Extraction
    extraction_result: CommunicationExtraction = chain.invoke({
        "job_context": job_context,
        "plan_meta": plan_meta_str,
        "transcript": transcript_json,
        "rubric": rubric_json
    })

    print("Running communication deterministic grading...")
    
    # Step 2: Deterministic processing
    # Build transcript lookup map for verification
    history_map = {t["turn_id"]: t["content"] for t in transcript_list}

    traits_output = {}
    traits_passed = 0
    traits_failed = 0
    traits_not_addressed = 0
    
    for trait_name in ["active_listening", "structure", "assertiveness", "clarity"]:
        trait_extract = getattr(extraction_result, trait_name, None)
        
        evidence_list = []
        pos_count = 0
        neg_count = 0
        
        if trait_extract:
            for pos in trait_extract.positive:
                turn_id = pos.turn_id or ""
                quote = pos.quote or ""
                verified = True
                
                if turn_id in history_map:
                    if quote not in history_map[turn_id]:
                        verified = False
                else:
                    verified = False
                    
                if verified:
                    pos_count += 1
                    
                evidence_list.append(CommEvidence(
                    signal_id=pos.signal_id,
                    turn_id=pos.turn_id,
                    quote=pos.quote,
                    polarity="positive"
                ))
                
            for neg in trait_extract.negative:
                turn_id = neg.turn_id or ""
                quote = neg.quote or ""
                verified = True
                
                if turn_id in history_map:
                    if quote not in history_map[turn_id]:
                        verified = False
                else:
                    verified = False
                    
                if verified:
                    neg_count += 1
                    
                evidence_list.append(CommEvidence(
                    signal_id=neg.signal_id,
                    turn_id=neg.turn_id,
                    quote=neg.quote,
                    polarity="negative"
                ))
        # Trait Calculations
        net_score = pos_count - neg_count
        total_evidence = pos_count + neg_count
        addressed = (total_evidence > 0)
        
        score = trait_score(net_score, total_evidence)
        
        is_passed = None
        if addressed:
            is_passed = (score >= 6.0)
            
        margin = abs(net_score)
        
        if not addressed:
            confidence = "low"
        elif total_evidence >= 3 and margin >= 2:
            confidence = "high"
        elif total_evidence >= 2 and margin >= 1:
            confidence = "medium"
        else:
            confidence = "low"
            
        # Update overall counters
        if addressed:
            if is_passed:
                traits_passed += 1
            else:
                traits_failed += 1
        else:
            traits_not_addressed += 1
            
        rationale = f"{pos_count} valid positive, {neg_count} valid negative signals. Net score: {net_score}, Trait score: {score}."
        
        traits_output[trait_name] = CommTraitEval(
            addressed=addressed,
            is_passed=is_passed,
            score=score,
            confidence=confidence,
            evidence=evidence_list,
            rationale=rationale
        )
        
    # Overall Aggregate Logic
    overall_is_passed = None
    rule_applied = ""
    
    if (traits_passed + traits_failed) > 0:
        if comm_weight.lower() == "high":
            rule_applied = "all_addressed_must_pass"
            overall_is_passed = (traits_failed == 0)
        else:
            rule_applied = "majority_pass"
            overall_is_passed = (traits_passed > traits_failed)
    else:
        rule_applied = "none_addressed"
        overall_is_passed = None
        
    # Aggregate confidence
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    rank_to_confidence = {0: "low", 1: "medium", 2: "high"}
    
    min_rank = 2
    has_addressed = False
    
    for trait_name, trait_eval in traits_output.items():
        if trait_eval.addressed:
            has_addressed = True
            rank = confidence_rank.get(trait_eval.confidence, 0)
            if rank < min_rank:
                min_rank = rank
                
    if has_addressed:
        aggregate_confidence = rank_to_confidence[min_rank]
    else:
        aggregate_confidence = "low"
        
    overall_output = CommOverallEval(
        is_passed=overall_is_passed,
        confidence=aggregate_confidence,
        traits_passed=traits_passed,
        traits_failed=traits_failed,
        traits_not_addressed=traits_not_addressed,
        rule_applied=rule_applied,
        rationale=f"{traits_passed} traits passed out of {traits_passed + traits_failed} addressed. Rule: {rule_applied}."
    )
    
    final_output = CommunicationOutput(
        communication=CommunicationOutputData(
            overall=overall_output,
            traits=traits_output
        )
    )

    return {
        "communication": final_output
    }
