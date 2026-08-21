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
    job_context: JobContext
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

        # Extract generated questions
        generated = result_state.get("consolidated_questions") or result_state.get("generated_questions", [])
        
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
    """
    logger.info(f"Received grading request for job: '{request.job_context.job_name}'")
    
    input_state = {
        "job_context": request.job_context.model_dump(),
        "plan_meta": request.plan_meta.model_dump(),
        "goals": [g.model_dump() for g in request.goals]
    }
    
    try:
        result_state = await grader_graph.ainvoke(input_state)
        
        # Return the final report, overall score, and recommendation
        return {
            "overall_score": result_state.get("overall_score"),
            "recommendation": result_state.get("recommendation"),
            "final_report": result_state.get("final_report"),
            "injection_findings": result_state.get("injection_findings")
        }
    except Exception as exc:
        logger.error(f"Error executing Grader Agent graph: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(exc)}"
        )
