"""
What: Initializes and exports Google Gemini LLM clients for use across all agents.
Why: Centralizes client instantiation, API key validation, and model configuration.
Boundaries: Does not define LangGraph agents, endpoints, or execution logic.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from the standard locations
load_dotenv()

# Verify that the API key is present in environment
_gemini_api_key = os.getenv("GEMINI_API_KEY")
if not _gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set in the environment or .env file.")

# Gemini 3.1 Flash-Lite: Cheap, extremely fast, ideal for planning, routing, and high-frequency checks.
gemini_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=_gemini_api_key,
    temperature=0.0,
)

# Gemini 3.5 Flash: Balanced model for general text processing and validation.
gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=_gemini_api_key,
    temperature=0.0,
)

# Gemini 3.1 Pro Preview: High reasoning capability, ideal for complex synthesis and strict schema generations.
gemini_pro = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    google_api_key=_gemini_api_key,
    temperature=0.0,
)
