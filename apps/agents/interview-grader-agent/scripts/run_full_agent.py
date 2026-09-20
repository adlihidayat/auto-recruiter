"""
What: CLI script to execute the full Interview Grader Agent pipeline on a custom candidate input payload.
Why: Provides a clean entrypoint to test full agent behavior (Phase 1 analysis + Phase 2 citation + Aggregation).
"""
import sys
import os
import json
import re
import importlib.util
from dotenv import load_dotenv

# Path resolution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(os.path.dirname(AGENT_DIR))

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, AGENT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))
if not os.getenv("GEMINI_API_KEY1") and os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY1"] = os.getenv("GEMINI_API_KEY")
if os.getenv("GEMINI_API_KEY1"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY1")

def load_submodule(fullname, path):
    if fullname in sys.modules:
        return sys.modules[fullname]
    spec = importlib.util.spec_from_file_location(fullname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = mod
    spec.loader.exec_module(mod)
    return mod

state_mod = load_submodule('interview_grader_agent.state', os.path.join(AGENT_DIR, 'state.py'))
sys.modules['..state'] = state_mod

prompts_mod = load_submodule('interview_grader_agent.prompts.aggregation_prompt', os.path.join(AGENT_DIR, 'prompts/aggregation_prompt.py'))
sys.modules['..prompts.aggregation_prompt'] = prompts_mod

prompts_core_mod = load_submodule('interview_grader_agent.prompts.core_analysis_prompt', os.path.join(AGENT_DIR, 'prompts/core_analysis_prompt.py'))
sys.modules['..prompts.core_analysis_prompt'] = prompts_core_mod

prompts_inj_mod = load_submodule('interview_grader_agent.prompts.injection_prompt', os.path.join(AGENT_DIR, 'prompts/injection_prompt.py'))
sys.modules['..prompts.injection_prompt'] = prompts_inj_mod

prompts_comm_mod = load_submodule('interview_grader_agent.prompts.communication_prompt', os.path.join(AGENT_DIR, 'prompts/communication_prompt.py'))
sys.modules['..prompts.communication_prompt'] = prompts_comm_mod

core_mod = load_submodule('interview_grader_agent.nodes.core_analysis', os.path.join(AGENT_DIR, 'nodes/core_analysis.py'))
sys.modules['..nodes.core_analysis'] = core_mod

comm_mod = load_submodule('interview_grader_agent.nodes.communication', os.path.join(AGENT_DIR, 'nodes/communication.py'))
sys.modules['..nodes.communication'] = comm_mod

inj_mod = load_submodule('interview_grader_agent.nodes.injection_check', os.path.join(AGENT_DIR, 'nodes/injection_check.py'))
sys.modules['..nodes.injection_check'] = inj_mod

agg_mod = load_submodule('interview_grader_agent.nodes.aggregation', os.path.join(AGENT_DIR, 'nodes/aggregation.py'))

from interview_grader_agent.state import GoalInput, PassingCriterion, WrongAnswerSignal, Interaction

def parse_string_criteria(criteria_str: str) -> list[PassingCriterion]:
    if not isinstance(criteria_str, str):
        return criteria_str
    results = []
    lines = [line.strip() for line in criteria_str.split("\n") if line.strip()]
    for line in lines:
        if ":" in line:
            c_id, text = line.split(":", 1)
            results.append(PassingCriterion(id=c_id.strip(), criteria=text.strip()))
        else:
            results.append(PassingCriterion(id=f"c_{len(results)+1:02d}", criteria=line.strip()))
    return results

def parse_string_signals(signals_str: str) -> list[WrongAnswerSignal]:
    if not isinstance(signals_str, str):
        return signals_str
    results = []
    lines = [line.strip() for line in signals_str.split("\n") if line.strip()]
    for line in lines:
        if ":" in line:
            s_id, text = line.split(":", 1)
            results.append(WrongAnswerSignal(id=s_id.strip(), signal=text.strip()))
        else:
            results.append(WrongAnswerSignal(id=f"w_{len(results)+1:02d}", signal=line.strip()))
    return results

def parse_string_transcript(transcript_raw) -> list[Interaction]:
    if isinstance(transcript_raw, list):
        parsed_list = []
        for idx, item in enumerate(transcript_raw):
            if isinstance(item, dict):
                t_id = item.get("turn_id", f"t_{idx+1:02d}")
                r = item.get("role", "candidate")
                c = item.get("content", "")
                parsed_list.append(Interaction(turn_id=t_id, role=r, content=c))
            elif hasattr(item, "role"):
                parsed_list.append(item)
        return parsed_list
    
    if not isinstance(transcript_raw, str):
        return []

    results = []
    pattern = r"\[(t_\d+)\]\s*(interviewer|candidate):\s*(.+?)(?=\[(t_\d+)\]|$)"
    matches = re.findall(pattern, transcript_raw, re.DOTALL)
    if matches:
        for m in matches:
            t_id, role, content = m[0], m[1], m[2].strip()
            results.append(Interaction(turn_id=t_id, role=role, content=content))
    else:
        # Fallback split by line
        for idx, line in enumerate(transcript_raw.split("\n")):
            line = line.strip()
            if not line: continue
            role = "interviewer" if line.startswith("interviewer:") else "candidate"
            content = line.split(":", 1)[-1].strip()
            results.append(Interaction(turn_id=f"t_{idx+1:02d}", role=role, content=content))
            
    return results

def normalize_goal(g_raw: dict) -> GoalInput:
    g_id = g_raw.get("goal_id", "g_01")
    topic = g_raw.get("topic", "Topic")
    goal_text = g_raw.get("goal", "Goal Description")
    grounding = g_raw.get("grounding_theory", "")
    weight = float(g_raw.get("weight", 1.0))
    
    criteria_raw = g_raw.get("criteria") or g_raw.get("passing_criteria", [])
    passing_criteria = parse_string_criteria(criteria_raw)
    
    signals_raw = g_raw.get("signals") or g_raw.get("wrong_answer_signals", [])
    wrong_answer_signals = parse_string_signals(signals_raw)
    
    history_raw = g_raw.get("interaction_history", [])
    interaction_history = parse_string_transcript(history_raw)
    
    return GoalInput(
        goal_id=g_id,
        topic=topic,
        goal=goal_text,
        passing_criteria=passing_criteria,
        wrong_answer_signals=wrong_answer_signals,
        pushback_triggers=[],
        grounding_theory=grounding,
        weight=weight,
        interaction_history=interaction_history
    )

from langsmith import traceable

@traceable(name="interview_grader_agent")
def run_full_pipeline(input_payload: dict):
    print("=" * 80)
    print(" EXECUTING FULL INTERVIEW GRADER AGENT PIPELINE ")
    print("=" * 80)
    
    # 1. Normalize goals
    raw_goals = input_payload.get("goals", [])
    normalized_goals = [normalize_goal(g) for g in raw_goals]
    
    state = {
        "job": input_payload.get("job", {
            "job_name": "Account Executive / CSM",
            "job_description": "Managing mid-market renewals and expansion."
        }),
        "plan_meta": input_payload.get("plan_meta", {
            "communication_weight": 0.3,
            "difficulty": "senior"
        }),
        "goals": normalized_goals,
        "core_analysis": None,
        "communication": None,
        "injection_check": None,
        "final_report": None
    }
    
    # Phase 1: Core Analysis, Communication, Injection Check
    print("\n[Phase 1] Executing Parallel Analysis Nodes...")
    
    core_res = core_mod.run_core_analysis(state)
    state.update(core_res)
    
    comm_res = comm_mod.run_communication(state)
    state.update(comm_res)
    
    inj_res = inj_mod.run_injection_check(state)
    state.update(inj_res)
    
    # Phase 2: Aggregation
    print("\n[Phase 2] Executing Aggregation Node...")
    agg_res = agg_mod.run_aggregation(state)
    report = agg_res["final_report"]
    
    print("\n" + "=" * 80)
    print(" FINAL AGENT REPORT OUTPUT ")
    print("=" * 80)
    print(f"Recommendation : {report.recommendation}")
    print(f"Composite Score: {report.composite_score}/10")
    print(f"Confidence     : {report.overall_confidence}")
    print(f"Graded At      : {report.graded_at}")
    print("\n--- REASONING SUMMARY ---")
    print(report.reasoning)
    print("\n" + "=" * 80)
    
    return report

if __name__ == "__main__":
    # Sample execution if run directly
    sample_input = {
        "job": {
            "job_name": "Customer Success Manager",
            "job_description": "Managing mid-market renewals ($50k-$300k ACV) and driving expansion."
        },
        "plan_meta": {
            "communication_weight": 0.3,
            "difficulty": "senior"
        },
        "goals": [
            {
                "goal_id": "g_ca_03",
                "topic": "Renewal Negotiations and Expansion Strategy",
                "goal": (
                    "Assess the candidate's methodology for conducting quarterly business reviews (QBRs), "
                    "managing renewal discussions for $50k-$300k ACV accounts, and identifying upsell "
                    "opportunities backed by product usage evidence."
                ),
                "grounding_theory": (
                    "# Renewal Negotiations and Expansion Strategy ($50k-$300k ACV)\n\n"
                    "Renewal execution should begin 90 to 120 days prior to contract expiration (T-120 to "
                    "T-90: internal health audit and stakeholder mapping; T-90: alignment meeting; T-60: "
                    "formal proposal; T-30: procurement/legal). Waiting until 30 days before expiration risks "
                    "last-minute churn surprises.\n\n"
                    "An effective QBR is structured around Executive Summary & Value Realization -- revisiting "
                    "KPIs and ROI -- rather than Feature-Dumping, which is walking through a laundry list of "
                    "new releases without tying them to the customer's ROI and business outcomes.\n\n"
                    "Expansion indicators like seat utilization at 90%+ capacity should be pitched by first "
                    "presenting the telemetry, then connecting the constraint to lost productivity or missed "
                    "business opportunity, before introducing the upgraded tier -- co-termed with the renewal "
                    "date. Pitching upsells arbitrarily based on account tenure or budget cycles, instead of "
                    "backing them with telemetry-driven business impact, is a pitfall."
                ),
                "criteria": (
                    "c_01: Outlines a structured pre-renewal timeline starting 90 to 120 days prior to "
                    "contract expiration (T-120 to T-90), AND explains that this early window is necessary for "
                    "internal account health audits and stakeholder mapping before formal proposals at T-60\n"
                    "c_02: Describes structuring the QBR around executive summary and value realization "
                    "metrics rather than feature-dumping, AND explains that this shifts the relationship from "
                    "a tactical tool provider to a strategic business partner\n"
                    "c_03: Identifies the 95% seat utilization telemetry as a concrete expansion trigger, AND "
                    "outlines an expansion pitch connecting that capacity constraint directly to lost "
                    "productivity or workflow bottlenecks before introducing an upgraded tier co-termed with "
                    "the renewal date"
                ),
                "signals": (
                    "w_01: Waits until 30 days before contract expiration to initiate renewal conversations or "
                    "send proposals\n"
                    "w_02: Conducts the QBR as a feature-dumping session showcasing a laundry list of new "
                    "product releases without tying them back to customer ROI and business outcomes\n"
                    "w_03: Pitches upsells or seat expansion arbitrarily based solely on account tenure or "
                    "budget cycles rather than backing the pitch with product telemetry data like seat "
                    "saturation or feature gating"
                ),
                "interaction_history": (
                    "[t_01] interviewer: Imagine you manage a key mid-market account with an ACV of $150,000 "
                    "whose annual contract is coming up for renewal in four months, and your telemetry shows "
                    "they are operating at 95 percent of their contracted seat capacity. Walk me through your "
                    "timeline and methodology for running their upcoming QBR, leading into a renewal and "
                    "expansion discussion.\n"
                    "[t_02] candidate: Honestly for an account this size I don't usually start the renewal "
                    "motion super early -- about 30 days out is normally enough runway to get the paperwork "
                    "through procurement and legal.\n"
                    "[t_03] interviewer: Okay, walk me through what the QBR itself looks like.\n"
                    "[t_04] candidate: In the QBR I mostly walk them through what we shipped that quarter -- "
                    "new integrations, the UI refresh, a couple of the bigger release notes -- so they can see "
                    "everything they're getting for their money.\n"
                    "[t_05] interviewer: You mentioned they're sitting at 95 percent of their seat capacity -- "
                    "how do you use that in the conversation?\n"
                    "[t_06] candidate: Yeah, since they're already coming up on renewal, that's usually a "
                    "natural point in their budget cycle to pitch more seats, so I'd just fold the expansion "
                    "ask into that same conversation."
                )
            }
        ]
    }
    
    run_full_pipeline(sample_input)
