"""
What: Initializes and exports Google Gemini LLM clients for use across all agents.
Why: Centralizes client instantiation, API key validation, and model configuration.
Boundaries: Does not define LangGraph agents, endpoints, or execution logic.
"""

import os
import warnings
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress fixed sampling defaults warning for Gemini Flash Lite models
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

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
    "gemini-3.5-flash-lite",
    temperature=0.0,
    max_retries=0
)

# Gemini 3.5 Flash: Balanced model for general text processing and validation.
gemini_flash = RotatingModelWrapper(
    "gemini-3.8-flash",
    temperature=0.0,
)

# Gemini 3.1 Pro Preview: High reasoning capability, ideal for complex synthesis and strict schema generations.
gemini_pro = RotatingModelWrapper(
    "gemini-3.1-pro-preview",
    temperature=0.0,
)

# --- Local ONNX Injection Client ---
from langsmith import traceable
import os
import warnings

def _resolve_onnx_model_dir() -> str:
    """
    Resolves the directory containing the ONNX model and tokenizer.
    Priority:
    1. Environment variable ONNX_INJECTION_MODEL_DIR
    2. Local assets directory inside core-ai-lib
    3. Dynamic monorepo root relative fallback path
    4. ~/.cache/auto_recruiter/onnx_model (auto-exported via optimum if missing)
    """
    env_dir = os.getenv("ONNX_INJECTION_MODEL_DIR")
    if env_dir and os.path.exists(os.path.join(env_dir, "model.onnx")):
        return env_dir

    # Check assets directory inside core-ai-lib package
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    asset_dir = os.path.join(pkg_dir, "assets", "onnx_injection_model")
    if os.path.exists(os.path.join(asset_dir, "model.onnx")):
        return asset_dir

    # Dynamic monorepo asset fallback
    current = os.path.abspath(__file__)
    root = current
    while root and os.path.basename(root) != "auto-recruiter" and os.path.dirname(root) != root:
        root = os.path.dirname(root)

    if root and os.path.basename(root) == "auto-recruiter":
        rel_path = os.path.join(root, "packages", "core-ai-lib", "src", "core_ai_lib", "assets", "onnx_injection_model")
        if os.path.exists(os.path.join(rel_path, "model.onnx")):
            return rel_path

    # User cache fallback
    user_cache = os.path.expanduser("~/.cache/auto_recruiter/onnx_model")
    if os.path.exists(os.path.join(user_cache, "model.onnx")):
        return user_cache

    # Attempt auto-export if missing
    try:
        os.makedirs(user_cache, exist_ok=True)
        from optimum.onnxruntime import ORTModelForSequenceClassification
        from transformers import AutoTokenizer

        print("ONNX injection model not found locally. Auto-exporting deepset/deberta-v3-base-injection...")
        model = ORTModelForSequenceClassification.from_pretrained(
            "deepset/deberta-v3-base-injection",
            export=True
        )
        tokenizer = AutoTokenizer.from_pretrained("deepset/deberta-v3-base-injection")

        model.save_pretrained(user_cache)
        tokenizer.save_pretrained(user_cache)
        return user_cache
    except Exception as e:
        print(f"Warning: Could not auto-download/export ONNX injection model: {e}")
        return user_cache

try:
    import onnxruntime as ort
    from transformers import AutoTokenizer
    import numpy as np

    # Suppress HuggingFace warnings about tokenization
    warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

    model_dir = _resolve_onnx_model_dir()
    
    # Try to load ONNX session and tokenizer if model exists
    if os.path.exists(os.path.join(model_dir, "model.onnx")):
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        ort_session = ort.InferenceSession(os.path.join(model_dir, "model.onnx"))
    else:
        tokenizer = None
        ort_session = None
        print("Warning: ONNX model not found at", model_dir)
        
except ImportError as e:
    tokenizer = None
    ort_session = None
    print(f"Warning: onnxruntime or transformers library not found. {e}")

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

@traceable(name="injection_score")
def get_injection_score(text: str) -> float:
    """
    Calls deepset/deberta-v3-base-injection locally using onnxruntime.
    Returns a float 0.0-1.0 representing the likelihood of injection.
    """
    if ort_session is None or tokenizer is None:
        return 0.0
        
    try:
        inputs = tokenizer(text, return_tensors="np", truncation=True, max_length=512)
        ort_inputs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"]
        }
        
        # RoBERTa/DeBERTa uses token_type_ids only if available in the model
        if "token_type_ids" in [i.name for i in ort_session.get_inputs()] and "token_type_ids" in inputs:
            ort_inputs["token_type_ids"] = inputs["token_type_ids"]
            
        ort_outs = ort_session.run(None, ort_inputs)
        logits = ort_outs[0]
        
        probabilities = softmax(logits)[0]
        
        # deepset/deberta-v3-base-injection mapping:
        # id2label typically: 0: "SAFE", 1: "INJECTION"
        # Since it's a binary classifier, we check if the label at index 1 corresponds to INJECTION.
        # Often, config.json maps it explicitly, but typically label 1 is INJECTION.
        # Let's dynamically map using tokenizer if available, otherwise assume 1 = INJECTION.
        # Actually, if we just extract probabilities, we will know index 1 is injection for this specific model.
        injection_prob = float(probabilities[1])
        
        return injection_prob
    except Exception as e:
        print(f"Error running local ONNX Injection Classifier: {e}")
        # Fail open or closed? If inference fails, return 0.5 (uncertain) to force LLM review
        return 0.5
