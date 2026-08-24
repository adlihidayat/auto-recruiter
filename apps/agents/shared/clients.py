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

keys = [
    os.getenv("GEMINI_API_KEY1"),
    os.getenv("GEMINI_API_KEY2"),
    os.getenv("GEMINI_API_KEY3")
]
valid_keys = [k for k in keys if k]
if not valid_keys:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        valid_keys = [key]

if not valid_keys:
    raise ValueError("No GEMINI_API_KEY found")

class RotatingModelWrapper:
    def __init__(self, model_name, **kwargs):
        self.clients = [
            ChatGoogleGenerativeAI(model=model_name, google_api_key=key, **kwargs)
            for key in valid_keys
        ]
        self.primary = self.clients[0]
        self.fallbacks = self.clients[1:]
        
    def invoke(self, *args, **kwargs):
        runnable = self.primary.with_fallbacks(self.fallbacks)
        return runnable.invoke(*args, **kwargs)
        
    def with_structured_output(self, schema):
        structured_primary = self.primary.with_structured_output(schema)
        structured_fallbacks = [c.with_structured_output(schema) for c in self.fallbacks]
        return structured_primary.with_fallbacks(structured_fallbacks)

    def bind_tools(self, tools, **kwargs):
        bound_primary = self.primary.bind_tools(tools, **kwargs)
        bound_fallbacks = [c.bind_tools(tools, **kwargs) for c in self.fallbacks]
        return bound_primary.with_fallbacks(bound_fallbacks)

# Gemini 3.1 Flash-Lite: Cheap, extremely fast, ideal for planning, routing, and high-frequency checks.
gemini_flash_lite = RotatingModelWrapper(
    "gemini-3.1-flash-lite",
    temperature=0.0,
    max_retries=0
)

# Gemini 3.5 Flash: Balanced model for general text processing and validation.
gemini_flash = RotatingModelWrapper(
    "gemini-3.5-flash",
    temperature=0.0,
)

# Gemini 3.1 Pro Preview: High reasoning capability, ideal for complex synthesis and strict schema generations.
gemini_pro = RotatingModelWrapper(
    "gemini-3.1-pro-preview",
    temperature=0.0,
)

# --- Local PromptGuard Client ---
from langsmith import traceable
import os

try:
    from transformers import pipeline
    import warnings
    # Suppress HuggingFace warnings about tokenization
    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
    
    hf_token = os.getenv("HF_TOKEN")
    
    prompt_guard = pipeline(
        "text-classification",
        model="meta-llama/Prompt-Guard-86M",
        token=hf_token
    )
except ImportError:
    prompt_guard = None
    print("Warning: transformers or torch library not found. Please install them to use PromptGuard locally.")

@traceable(name="prompt_guard_score")
def get_prompt_guard_score(text: str) -> float:
    """
    Calls meta-llama/Prompt-Guard-86M locally using transformers pipeline.
    Returns a float 0.0-1.0 representing the likelihood of injection or jailbreak.
    """
    if prompt_guard is None:
        raise ValueError("prompt_guard pipeline is not initialized. Ensure transformers and torch are installed.")
        
    try:
        # top_k=None returns all scores
        results = prompt_guard(text, top_k=None)
        
        malicious_score = 0.0
        if isinstance(results, list) and isinstance(results[0], list):
            results = results[0]
            
        for res in results:
            label = res.get('label', '')
            score = res.get('score', 0.0)
            
            if label.upper() in ["INJECTION", "JAILBREAK"]:
                malicious_score += score
                
        return min(malicious_score, 1.0)
    except Exception as e:
        print(f"Error running local PromptGuard: {e}")
        # Fail open or closed? If inference fails, return 0.5 (uncertain) to force LLM review
        return 0.5
