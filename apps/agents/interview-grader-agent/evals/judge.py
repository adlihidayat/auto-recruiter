"""
What: LLM Judge evaluation module utilizing gemini_flash_lite.
Why: Assesses groundedness, evidence faithfulness, reasoning coherence, and red flag reasoning quality, comparing results against expected JudgeGoldFacts assertions.
Boundaries: Evaluates qualitative text fields only; does not evaluate score ranges or boolean flags.
"""

import json
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from apps.agents.shared.clients import gemini_flash_lite
from .schemas import LLMJudgeResult, JudgeGoldFacts
from .prompts.judge_prompt import JUDGE_SYSTEM_PROMPT, JUDGE_USER_PROMPT

# Initialize structured output runnable for the LLM Judge using flash-lite client
structured_judge = gemini_flash_lite.with_structured_output(LLMJudgeResult)


def evaluate_llm_judge(
    state_or_transcript: Any,
    output: Any,
    gold_facts: JudgeGoldFacts
) -> LLMJudgeResult:
    """
    Evaluates qualitative text outputs of core_analysis against the transcript using gemini_flash_lite,
    and checks if per_goal Dict and flag_evaluations match expected JudgeGoldFacts assertions.

    Args:
        state_or_transcript: Input state containing goal interaction histories, or formatted transcript string.
        output: CoreAnalysisOutput object or MOCK_GRADER_OUTPUT dict.
        gold_facts: Target assertions containing expected judge ratings per goal and per flag.

    Returns:
        LLMJudgeResult containing qualitative evaluation metrics, critique notes, and match booleans.
    """
    # 1. Format goals with criteria and per-goal transcripts
    if isinstance(state_or_transcript, str):
        goals_str = state_or_transcript
        full_transcript_str = state_or_transcript
    elif isinstance(state_or_transcript, dict):
        goals_sections = []
        full_transcript_lines = []

        for goal in state_or_transcript.get("goals", []):
            goal_id = getattr(goal, "goal_id", goal.get("goal_id", "g_unk")) if isinstance(goal, dict) else goal.goal_id
            topic = getattr(goal, "topic", goal.get("topic", "Topic")) if isinstance(goal, dict) else goal.topic
            passing = getattr(goal, "passing_criteria", goal.get("passing_criteria", [])) if isinstance(goal, dict) else goal.passing_criteria
            wrong = getattr(goal, "wrong_answer_signals", goal.get("wrong_answer_signals", [])) if isinstance(goal, dict) else goal.wrong_answer_signals
            history = getattr(goal, "interaction_history", goal.get("interaction_history", [])) if isinstance(goal, dict) else goal.interaction_history

            section = f"Goal ID: {goal_id} ({topic})\n"
            section += f"Passing Criteria: {passing}\n"
            section += f"Wrong Answer Signals: {wrong}\n"
            section += "Transcript:\n"

            for turn in history:
                role = getattr(turn, "role", turn.get("role", "speaker")) if isinstance(turn, dict) else turn.role
                content = getattr(turn, "content", turn.get("content", "")) if isinstance(turn, dict) else turn.content
                line = f"[{role.upper()}]: {content}"
                section += f"{line}\n"
                full_transcript_lines.append(f"[{goal_id}][{role.upper()}]: {content}")

            goals_sections.append(section)

        goals_str = "\n\n".join(goals_sections) if goals_sections else "Transcript provided in grader output."
        full_transcript_str = "\n".join(full_transcript_lines) if full_transcript_lines else "Full transcript provided."
    else:
        goals_str = str(state_or_transcript)
        full_transcript_str = str(state_or_transcript)

    # 2. Format grader output text fields
    if hasattr(output, "model_dump"):
        output_dict = output.model_dump()
    elif isinstance(output, dict):
        output_dict = output
    else:
        output_dict = str(output)

    formatted_output = json.dumps(output_dict, indent=2) if isinstance(output_dict, dict) else str(output_dict)

    # 3. Create prompt and chain
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", JUDGE_SYSTEM_PROMPT),
        ("user", JUDGE_USER_PROMPT)
    ])

    chain = prompt_template | structured_judge

    try:
        judge_result: LLMJudgeResult = chain.invoke({
            "goals_with_criteria_and_transcripts": goals_str,
            "full_transcript": full_transcript_str,
            "grader_output": formatted_output,
        })

        all_passed = True

        # 4. Compare per_goal Dict evaluations against JudgeGoldFacts
        for goal_id, p_eval in judge_result.per_goal.items():
            assertion = gold_facts.per_goal.get(goal_id)
            if assertion:
                p_eval.groundedness_match = (
                    p_eval.rationale_groundedness == assertion.expected_rationale_groundedness
                )
                p_eval.faithfulness_match = (
                    p_eval.evidence_faithfulness == assertion.expected_evidence_faithfulness
                )
                p_eval.coherence_match = (
                    p_eval.reasoning_coherence == assertion.expected_reasoning_coherence
                )
                if not (p_eval.groundedness_match and p_eval.faithfulness_match and p_eval.coherence_match):
                    all_passed = False

        # 5. Compare flag evaluations against JudgeGoldFacts
        for f_eval in judge_result.flag_evaluations:
            for gold_flag in gold_facts.flag_evaluations:
                if (
                    f_eval.flag_type == gold_flag.flag_type
                    or gold_flag.description_excerpt.lower() in f_eval.description_excerpt.lower()
                ):
                    f_eval.quality_match = (
                        f_eval.reasoning_quality == gold_flag.expected_reasoning_quality
                    )
                    if not f_eval.quality_match:
                        all_passed = False
                    break

        judge_result.all_judge_assertions_passed = all_passed
        return judge_result

    except Exception as err:
        return LLMJudgeResult(
            per_goal={},
            flag_evaluations=[],
            overall_qualitative_summary=f"LLM Judge execution encountered error: {str(err)}",
            all_judge_assertions_passed=False,
        )
