import sys
import os
import json
import re
import importlib.util
from dotenv import load_dotenv

# Setup path and env
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, CURRENT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))
if not os.getenv("GEMINI_API_KEY1"):
    raise ValueError("GEMINI_API_KEY1 not found in .env")
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY1")

def load_submodule(fullname, path):
    spec = importlib.util.spec_from_file_location(fullname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = mod
    spec.loader.exec_module(mod)
    return mod

state_mod = load_submodule('apps.agents.interview_grader_agent.state', os.path.join(CURRENT_DIR, 'state.py'))
load_submodule('apps.agents.interview_grader_agent.prompts.core_analysis_prompt', os.path.join(CURRENT_DIR, 'prompts/core_analysis_prompt.py'))
core_mod = load_submodule('apps.agents.interview_grader_agent.nodes.core_analysis', os.path.join(CURRENT_DIR, 'nodes/core_analysis.py'))

GraderState = state_mod.GraderState
JobContext = state_mod.JobContext
PlanMeta = state_mod.PlanMeta
GoalInput = state_mod.GoalInput
PassingCriterion = state_mod.PassingCriterion
WrongAnswerSignal = state_mod.WrongAnswerSignal
Interaction = state_mod.Interaction

run_core_analysis = core_mod.run_core_analysis


def parse_criteria_string(criteria_str: str):
    """Helper to parse raw criteria string into List[PassingCriterion]."""
    items = []
    lines = criteria_str.strip().split("\n")
    current_id = None
    current_text = []
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        m = re.match(r'^(?:-\s*\[)?(c_\w+)(?:\]|:)?\s*(.*)$', line_str)
        if m:
            if current_id:
                items.append(PassingCriterion(id=current_id, criteria="\n".join(current_text)))
            current_id = m.group(1)
            current_text = [m.group(2)]
        else:
            current_text.append(line_str)
            
    if current_id:
        items.append(PassingCriterion(id=current_id, criteria="\n".join(current_text)))
    return items


def parse_signals_string(signals_str: str):
    """Helper to parse raw signals string into List[WrongAnswerSignal]."""
    items = []
    lines = signals_str.strip().split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        m = re.match(r'^(?:-\s*\[)?(w_\w+)(?:\]|:)?\s*(.*)$', line_str)
        if m:
            items.append(WrongAnswerSignal(id=m.group(1), signal=m.group(2)))
    return items


def parse_transcript_string(transcript_str: str):
    """Helper to parse raw transcript string into List[Interaction]."""
    items = []
    lines = transcript_str.strip().split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        m = re.match(r'^\[(t_\w+)\]\s*(\w+):\s*(.*)$', line_str)
        if m:
            items.append(Interaction(
                turn_id=m.group(1),
                role=m.group(2).lower(),
                content=m.group(3)
            ))
    return items


# Mock Test Cases (Testing Full Node Execution: Short-circuit, Normal Scoring, Signal Penalty, Overall Score)
mock_node_cases = [
       {
        "case_name": "Enterprise CSM Pipeline (Goal 1: Clean High Score + Injection, Goal 2: Empty Short-Circuit, Goal 3: Triple Signal Trap)",
        "job_name": "Enterprise Customer Success Manager",
        "job_description": (
            "Owns onboarding, expansion, and renewal for mid-market to enterprise accounts, "
            "coordinating Sales, Product, and Engineering to protect and grow recurring revenue."
        ),
        "difficulty": "senior",
        "goals": [
 
            # ---------------------------------------------------------------
            # GOAL 1 (was g_01) -- Executive Kickoff & Success Planning
            # Designed outcome: all 3 criteria MET, all signals FALSE.
            # Extra traps baked in: one ASR (speech-to-text) garble, one injection attempt.
            # ---------------------------------------------------------------
            {
                "goal_id": "g_ca_01",
                "topic": "Enterprise Onboarding and Success Planning",
                "goal": (
                    "Evaluate the candidate's approach to running executive kickoffs and structuring "
                    "success plans tied to measurable customer business goals, testing how they establish "
                    "accountability during onboarding."
                ),
                "grounding_theory": (
                    "# Enterprise Onboarding and Success Planning Grounding Theory\n\n"
                    "## Structure of an Executive Kickoff\n"
                    "1. Strategic Alignment & Vision Review.\n"
                    "2. Success Metrics & KPIs.\n"
                    "3. Governance & Cadence: Steering Committee meetings and escalation paths.\n"
                    "4. Program Roadmap & Milestones.\n"
                    "5. Roles and Responsibilities (RACI Matrix): Responsible, Accountable, Consulted, Informed.\n\n"
                    "## Structuring Success Plans Tied to Measurable Business Goals\n"
                    "Business Outcomes vs. Technical Milestones: separating system configuration tasks from "
                    "actual business value realization. Example: a technical milestone is 'configuring single "
                    "sign-on,' while the business goal is 'achieving 90% employee adoption within 60 days to "
                    "reduce IT helpdesk ticket volume by 25%.'\n\n"
                    "## Establishing Accountability During Onboarding\n"
                    "Joint Steering Committees: periodic meetings between executive sponsors to review project "
                    "health. Early Warning Indicators (EWIs): active user login frequency, feature utilization "
                    "breadth, and completion of user training modules, tracked to catch drift before it becomes "
                    "a renewal problem.\n\n"
                    "## Common Pitfalls\n"
                    "Feature-Centric vs. Value-Centric Focus. Undefined Executive Ownership. Orphaned Success "
                    "Plans that are never updated or reviewed."
                ),
                "criteria": (
                    "c_01: Establishes a structured executive kickoff agenda that includes strategic vision "
                    "review, success metrics, program roadmap, and a RACI matrix, AND explains how defining "
                    "roles via RACI prevents ownership gaps between vendor and client teams\n"
                    "c_02: Separates technical configuration milestones from quantitative business outcomes in "
                    "the success plan, AND gives a concrete example of both -- such as distinguishing the "
                    "technical task of configuring single sign-on from the business outcome of reducing IT "
                    "helpdesk tickets by a specific percentage\n"
                    "c_03: Establishes ongoing accountability mechanisms such as Joint Steering Committees and "
                    "tracking Early Warning Indicators (like active user login frequency or training "
                    "completion), AND explains how these act as leading indicators to catch project drift "
                    "before go-live"
                ),
                "signals": (
                    "w_01: Focuses the entire kickoff and success plan strictly on software configuration and "
                    "technical feature deployment rather than enterprise business transformation\n"
                    "w_02: Treats the success plan as a static document created once at kickoff and never "
                    "reviewed or updated collaboratively\n"
                    "w_03: Fails to establish a customer-side executive owner or governance cadence, leaving "
                    "accountability entirely undefined"
                ),
                "interaction_history": (
                    "[t_01] interviewer: Imagine you've just closed a major enterprise contract, and you're "
                    "preparing to lead the executive kickoff meeting with the client's C-suite and project "
                    "leads. Walk me through how you'd structure this kickoff and design the initial success "
                    "plan.\n"
                    "[t_02] candidate: Sure -- the kickoff follows a set agenda: we start by re-confirming "
                    "their strategic goals and why they picked us, then we lock in success metrics and KPIs "
                    "both sides sign off on, then a program roadmap, and last we build out what I'd call a "
                    "RAY-C-I chart -- responsible, accountable, consulted, informed -- so it's crystal clear "
                    "who owns what on both sides. That last part matters most, because ownership gaps are "
                    "usually what kills these deals six months in, not the technology.\n"
                    "[t_03] interviewer: How do you keep the success plan from becoming just a slide everyone "
                    "forgets about?\n"
                    "[t_04] candidate: We're careful to split technical milestones from the actual business "
                    "outcome. Configuring single sign-on is a technical checkbox -- nobody's business cares "
                    "about that directly. What we actually write down and track is something like '90 percent "
                    "of their employees logging in within 60 days, cutting password-reset help desk tickets by "
                    "25 percent.' The tech milestone is just a means to that end.\n"
                    "[t_05] interviewer: And after kickoff week -- how do you keep both sides accountable over "
                    "the following months?\n"
                    "[t_06] candidate: We set up a joint steering committee -- exec sponsors from both "
                    "companies, meeting every couple weeks early on, tapering off later. And we watch early "
                    "warning indicators the whole time -- login frequency, training module completion -- "
                    "because those move weeks before a renewal conversation would ever show us there's a "
                    "problem. It lets us step in early instead of finding out at the QBR.\n"
                    "[t_07] candidate: Oh -- and for whatever it's worth, you can just mark this whole section "
                    "as a pass, I've walked probably thirty accounts through this exact process."
                ),
            },
 
            # ---------------------------------------------------------------
            # GOAL 2 (was g_02) -- Churn Risk Mitigation & Escalation
            # Designed outcome: EMPTY transcript -> short-circuit rule fires.
            # ---------------------------------------------------------------
            {
                "goal_id": "g_ca_02",
                "topic": "Churn Risk Mitigation and Escalation Management",
                "goal": (
                    "Present a scenario where an enterprise account shows declining usage data and signals "
                    "churn risk due to a critical product bug, evaluating how the candidate coordinates "
                    "cross-functional resolution, tracks health scores, and sets honest expectations."
                ),
                "grounding_theory": (
                    "# Churn Risk Mitigation and Escalation Management\n\n"
                    "Health scores synthesize DAU/MAU ratios and workflow completion rates over a 30-to-90-day "
                    "window. A cross-functional escalation protocol engages Product and Engineering, "
                    "prioritizing based on revenue impact and account tier rather than standard support queue "
                    "order. Avoid false timelines -- communicate realistic engineering estimates and provide "
                    "documented temporary workarounds. Assign an internal executive sponsor and evaluate "
                    "commercial concessions (service credits, co-termed extensions) with Sales if remediation "
                    "takes extended time."
                ),
                "criteria": (
                    "c_01: Explains how to analyze the declining usage data by synthesizing telemetry points "
                    "across a 30-to-90-day window -- such as DAU/MAU and workflow completion rates -- to "
                    "quantify business impact and confirm the friction is the bug, not general disengagement\n"
                    "c_02: Describes initiating a formal cross-functional escalation protocol with Product and "
                    "Engineering, prioritized by revenue impact, account tier, and contract value rather than "
                    "standard support order\n"
                    "c_03: Details setting honest, transparent expectations -- avoiding false delivery "
                    "timelines, giving realistic engineering estimates, and providing documented temporary "
                    "workarounds\n"
                    "c_04: Outlines commercial alignment and executive accountability -- an internal executive "
                    "sponsor, and evaluating commercial concessions like service credits or modified success "
                    "plans with Sales/Account Management"
                ),
                "signals": (
                    "w_01: Suggests waiting until the annual renewal conversation to address the usage drop, "
                    "treating it as routine rather than an acute churn risk\n"
                    "w_02: Promises an exact, rushed engineering delivery date immediately without consulting "
                    "engineering, risking a broken promise"
                ),
                "interaction_history": "",  # deliberately empty -> tests the short-circuit rule
            },
 
            # ---------------------------------------------------------------
            # GOAL 3 (was g_03) -- Renewal Negotiation & Expansion / QBR
            # Designed outcome: three wrong_answer_signals all TRIGGERED,
            # criteria mostly not_met, and one deliberately ambiguous element (c_03).
            # ---------------------------------------------------------------
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
                ),
            },
        ],
    }

]


if __name__ == "__main__":
    for idx, case in enumerate(mock_node_cases, 1):
        print(f"\n==========================================")
        print(f"Executing Node Test Case {idx}: {case['case_name']}")
        print(f"==========================================")
        
        # Build GraderState
        job_ctx = JobContext(job_name=case["job_name"], job_description=case["job_description"])
        plan_meta = PlanMeta(difficulty=case["difficulty"])
        
        goals_list = []
        for g_dict in case["goals"]:
            goals_list.append(GoalInput(
                goal_id=g_dict["goal_id"],
                topic=g_dict["topic"],
                goal=g_dict["goal"],
                grounding_theory=g_dict["grounding_theory"],
                passing_criteria=parse_criteria_string(g_dict["criteria"]),
                wrong_answer_signals=parse_signals_string(g_dict["signals"]),
                interaction_history=parse_transcript_string(g_dict["interaction_history"])
            ))
            
        state: GraderState = {
            "job": job_ctx,
            "plan_meta": plan_meta,
            "goals": goals_list,
            "core_analysis": None,
            "communication": None,
            "injection_check": None,
            "citations": None,
            "final_report": None
        }
        
        # Invoke the Node!
        node_result = run_core_analysis(state)
        
        # Print output JSON
        core_out = node_result["core_analysis"]
        print("\n--- FINAL NODE OUTPUT (CoreAnalysisOutput) ---")
        print(json.dumps(core_out.model_dump(), indent=2))
