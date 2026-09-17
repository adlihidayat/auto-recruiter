"""
What: Configures LangSmith tracing environment variables and exports tracing helpers.
Why: Ensures that all agent operations and node executions are logged to LangSmith for observability.
Boundaries: Does not define the models or graph execution logic directly.
"""

import os
from dotenv import load_dotenv
from langsmith import traceable

# Load environment variables
load_dotenv()

def verify_tracing_setup() -> bool:
    """
    Checks if LangSmith tracing environment variables are correctly configured.
    
    Returns:
        bool: True if tracing is active and configured, False otherwise.
    """
    is_tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    api_key_exists = bool(os.getenv("LANGCHAIN_API_KEY"))
    project_exists = bool(os.getenv("LANGCHAIN_PROJECT"))
    
    return is_tracing_enabled and api_key_exists and project_exists

# Export traceable decorator for use on custom tools and helper nodes
__all__ = ["traceable", "verify_tracing_setup"]
