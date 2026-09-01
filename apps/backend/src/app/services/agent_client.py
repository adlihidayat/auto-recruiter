"""
What: HTTP Client for communicating with apps/agents service over HTTP.
Why: Enforces strict boundary between core backend and AI agents container layer.
Boundaries: Sends HTTP requests to AGENTS_SERVICE_URL; does not import agent graph files directly.
"""

import logging
from typing import Dict, Any
import httpx

from app.core.config import application_settings

logger = logging.getLogger("agent-client")

async def request_question_suite_from_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends HTTP POST to apps/agents to trigger Question-Maker Agent execution.
    
    Args:
        payload: Dict containing job_name, job_description, difficulty, num_goals, total_duration_minutes.
        
    Returns:
        Dict containing generated 'questions' array.
    """
    url = f"{application_settings.AGENTS_SERVICE_URL}/api/question-maker/generate"
    logger.info(f"Sending HTTP POST to Agent Service: {url} for job '{payload.get('job_name')}'")
    
    DEFAULT_ERROR = "Failed to generate interview plan. Please try again or simplify your job description."

    # 5-minute timeout for web search & LLM generation
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(url, json=payload)
        except Exception as err:
            logger.error(f"HTTP Connection to Agent Service failed: {err}")
            raise RuntimeError(DEFAULT_ERROR) from err
        
        if response.status_code != 200:
            error_detail = DEFAULT_ERROR
            try:
                err_json = response.json()
                if isinstance(err_json, dict) and "detail" in err_json:
                    detail_str = str(err_json["detail"]).strip()
                    if detail_str:
                        error_detail = detail_str
            except Exception:
                if response.text and len(response.text.strip()) < 300:
                    error_detail = response.text.strip()
                    
            logger.error(f"Agent Service HTTP Error ({response.status_code}): {error_detail}")
            raise RuntimeError(error_detail)
            
        return response.json()

async def request_grading_from_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends HTTP POST to apps/agents to trigger Interview Grader Agent execution.
    """
    url = f"{application_settings.AGENTS_SERVICE_URL}/api/grader/evaluate"
    logger.info(f"Sending HTTP POST to Agent Service: {url} for grading candidate.")
    
    # 5-minute timeout for LLM generation
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            logger.error(f"Agent Service HTTP Error ({response.status_code}): {response.text}")
            raise RuntimeError(f"Agent Service returned error status {response.status_code}: {response.text}")
            
        return response.json()
