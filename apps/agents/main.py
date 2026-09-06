"""
What: Agent Service FastAPI application factory and entrypoint.
Why: Exposes non-realtime HTTP endpoints (question-maker, interviewer, grader) to the core backend server.
Boundaries: Does not touch core backend database or frontend HTTP routes directly.
"""

import os
import sys
import logging
from typing import Literal, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure root and agents directory are in Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AGENTS_DIR = os.path.abspath(os.path.dirname(__file__))
QM_DIR = os.path.join(AGENTS_DIR, "question-maker-agent")

for p in [ROOT_DIR, AGENTS_DIR, QM_DIR]:
    if p not in sys.path:
        sys.path.append(p)

# Load environment credentials
load_dotenv(os.path.join(AGENTS_DIR, ".env"))

import importlib
qm_graph_module = importlib.import_module("question-maker-agent.graph")
question_maker_graph = qm_graph_module.graph

grader_graph_module = importlib.import_module("interview-grader-agent.graph")
grader_graph = grader_graph_module.create_grader_graph()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agents-service")

app = FastAPI(
    title="Auto Recruiter Agents Service",
    version="1.0.0",
    description="HTTP microservice serving LangGraph agents (question-maker, grader)."
)

# --- Schemas ---

class QuestionMakerRequest(BaseModel):
    job_name: str
    job_description: str
    difficulty: Literal["junior", "mid", "senior", "lead", "infer"] = "mid"
    num_goals: int = 4
    total_duration_minutes: int = 30

class ReferenceSourceSchema(BaseModel):
    url: str
    title: str
    excerpt: str
    matched_query: str
    credibility_tier: str
    corroborated: bool

class PushbackTriggerSchema(BaseModel):
    trigger: str
    severity: str
    pushback_type: str

class QuestionItemSchema(BaseModel):
    goal_id: str
    topic: str
    goal: str
    suggested_opening: str
    passing_criteria: List[str] = []
    pushback_triggers: List[PushbackTriggerSchema] = []
    wrong_answer_signals: List[str] = []
    grounding_theory: Optional[str] = None
    references: List[ReferenceSourceSchema] = []

class QuestionSuiteResponse(BaseModel):
    questions: List[QuestionItemSchema]

grader_state_module = importlib.import_module("interview-grader-agent.state")
JobContext = grader_state_module.JobContext
PlanMeta = grader_state_module.PlanMeta
GoalInput = grader_state_module.GoalInput

class GraderRequest(BaseModel):
    job: JobContext
    plan_meta: PlanMeta
    goals: List[GoalInput]

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agents"}

def _extract_val(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        val = obj.get(key)
        return val if val is not None else default
    try:
        val = getattr(obj, key, None)
        return val if val is not None else default
    except Exception:
        return default

@app.post("/api/question-maker/generate", response_model=QuestionSuiteResponse)
async def generate_question_suite(request: QuestionMakerRequest):
    """
    Invokes the Question-Maker Agent LangGraph workflow to plan, retrieve grounding, generate, and validate interview goals.
    """
    logger.info(f"Received question generation request for position: '{request.job_name}'")
    
    input_state = {
        "job_name": request.job_name,
        "job_description": request.job_description,
        "difficulty": request.difficulty,
        "num_goals": request.num_goals,
        "total_duration_minutes": request.total_duration_minutes,
    }
    
    try:
        result_state = await question_maker_graph.ainvoke(input_state)
        
        # Build mapping of grounding theories & references
        theories_map = {}
        for t in result_state.get("grounding_theories", []):
            gid = _extract_val(t, "goal_id")
            theories_map[gid] = t

        # Extract questions from final_suite (deduplicated, latest revision per goal_id).
        # Falling back to generated_questions would include all retry/revision history — do NOT do that.
        final_suite = result_state.get("final_suite")
        if final_suite:
            # final_suite may be a QuestionSuite Pydantic model or a plain dict depending on LangGraph serialization
            if isinstance(final_suite, dict):
                generated = final_suite.get("questions", [])
            else:
                generated = getattr(final_suite, "questions", [])
        else:
            # Guard: assemble_node did not run (graph exited early); surface nothing rather than raw accumulator
            generated = []
        
        questions_output = []
        for q in generated:
            gid = _extract_val(q, "goal_id")
            theory_obj = theories_map.get(gid)
            
            theory_text = _extract_val(q, "grounding_theory")
            if not theory_text and theory_obj:
                theory_text = _extract_val(theory_obj, "theory")
                
            refs = []
            if theory_obj:
                raw_refs = _extract_val(theory_obj, "references", [])
                for r in raw_refs:
                    refs.append(ReferenceSourceSchema(
                        url=_extract_val(r, "url", ""),
                        title=_extract_val(r, "title", ""),
                        excerpt=_extract_val(r, "excerpt", ""),
                        matched_query=_extract_val(r, "matched_query", ""),
                        credibility_tier=_extract_val(r, "credibility_tier", "A"),
                        corroborated=_extract_val(r, "corroborated", True),
                    ))

            p_triggers = []
            raw_triggers = _extract_val(q, "pushback_triggers", [])
            for pt in raw_triggers:
                p_triggers.append(PushbackTriggerSchema(
                    trigger=_extract_val(pt, "trigger", ""),
                    severity=_extract_val(pt, "severity", "critical"),
                    pushback_type=_extract_val(pt, "pushback_type", "concrete"),
                ))

            item = QuestionItemSchema(
                goal_id=gid or "",
                topic=_extract_val(q, "topic", ""),
                goal=_extract_val(q, "goal", ""),
                suggested_opening=_extract_val(q, "suggested_opening", ""),
                passing_criteria=_extract_val(q, "passing_criteria", []),
                pushback_triggers=p_triggers,
                wrong_answer_signals=_extract_val(q, "wrong_answer_signals", []),
                grounding_theory=theory_text,
                references=refs
            )
            questions_output.append(item)
            
        logger.info(f"Successfully generated {len(questions_output)} questions for '{request.job_name}'")
        return QuestionSuiteResponse(questions=questions_output)

    except Exception as exc:
        logger.error(f"Error executing Question-Maker Agent graph: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(exc)}"
        )

@app.post("/api/grader/evaluate")
async def evaluate_candidate(request: GraderRequest):
    """
    Invokes the Interview Grader Agent LangGraph workflow.
    Returns a fully structured evaluation: final report, per-goal core analysis
    with merged citations, communication trait breakdown, and injection findings.
    """
    logger.info(f"Received grading request for job: '{request.job.job_name}'")
    
    input_state = {
        "job": request.job.model_dump(),
        "plan_meta": request.plan_meta.model_dump(),
        "goals": [g.model_dump() for g in request.goals]
    }
    
    try:
        result_state = await grader_graph.ainvoke(input_state)
        
        # --- final_report ---
        final_report = result_state.get("final_report")
        if hasattr(final_report, "model_dump"):
            final_report_dict = final_report.model_dump()
        elif isinstance(final_report, dict):
            final_report_dict = final_report
        else:
            final_report_dict = {}

        # --- injection_check ---
        injection_check = result_state.get("injection_check")
        if hasattr(injection_check, "model_dump"):
            injection_dict = injection_check.model_dump()
        elif isinstance(injection_check, dict):
            injection_dict = injection_check
        else:
            injection_dict = {}

        # --- communication_analysis ---
        # The "communication" node returns {"communication": CommunicationOutput(...)}.
        # LangGraph merges that into state["communication"] — a CommunicationOutput Pydantic model.
        # CommunicationOutput.communication is a CommunicationOutputData that has .overall and .traits.
        comm_state = result_state.get("communication")
        if hasattr(comm_state, "model_dump"):
            # CommunicationOutput.model_dump() -> {"communication": {"overall": ..., "traits": ...}}
            comm_dict = comm_state.model_dump().get("communication", {})
        elif isinstance(comm_state, dict):
            # May already be unwrapped or raw dict
            comm_dict = comm_state.get("communication", comm_state)
        else:
            comm_dict = {}

        # --- core_analysis + citations merged per goal ---
        # Build a fast lookup: goal_id -> list of Citation dicts from the citations node
        citations_output = result_state.get("citations")
        citations_by_goal: dict = {}
        if hasattr(citations_output, "goal_citations"):
            for gc in citations_output.goal_citations:
                gid = gc.goal_id if hasattr(gc, "goal_id") else gc.get("goal_id", "")
                raw_cits = gc.citations if hasattr(gc, "citations") else gc.get("citations", [])
                citations_by_goal[gid] = [
                    (c.model_dump() if hasattr(c, "model_dump") else c) for c in raw_cits
                ]
        elif isinstance(citations_output, dict):
            for gc in citations_output.get("goal_citations", []):
                gid = gc.get("goal_id", "")
                citations_by_goal[gid] = gc.get("citations", [])

        core_analysis = result_state.get("core_analysis")
        if hasattr(core_analysis, "model_dump"):
            raw_goals = core_analysis.model_dump().get("goals", [])
        elif isinstance(core_analysis, dict):
            raw_goals = core_analysis.get("goals", [])
        else:
            raw_goals = []

        # Merge citations into each goal dict
        goals_with_citations = []
        for goal_eval in raw_goals:
            if hasattr(goal_eval, "model_dump"):
                goal_dict = goal_eval.model_dump()
            elif isinstance(goal_eval, dict):
                goal_dict = goal_eval
            else:
                continue
            gid = goal_dict.get("goal_id", "")
            goal_dict["citations"] = citations_by_goal.get(gid, [])
            goals_with_citations.append(goal_dict)

        return {
            "overall_score": final_report_dict.get("composite_score"),
            "recommendation": final_report_dict.get("recommendation"),
            "final_report": final_report_dict,
            "injection_findings": injection_dict.get("injection_findings", []),
            "communication": comm_dict,
            "goals": goals_with_citations,
        }

    except Exception as exc:
        logger.error(f"Error executing Grader Agent graph: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(exc)}"
        )
