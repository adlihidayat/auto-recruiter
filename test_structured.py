import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('apps/agents'))
from dotenv import load_dotenv
load_dotenv(".env")

import importlib
interviewer_state = importlib.import_module("interviewer-agent.state")
InterviewerDecision = interviewer_state.InterviewerDecision

from apps.agents.shared.clients import gemini_flash_lite
structured_llm_client = gemini_flash_lite.with_structured_output(InterviewerDecision)

try:
    res = structured_llm_client.invoke("The user says hi. Give a decision to advance.")
    print("Success:", res)
    print("Type:", type(res))
except Exception as e:
    import traceback
    traceback.print_exc()
