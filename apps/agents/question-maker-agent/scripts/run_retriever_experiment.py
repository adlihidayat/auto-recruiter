import os
import sys
import json
import importlib
from typing import Optional, Literal
from pydantic import BaseModel, Field

os.environ["LANGCHAIN_PROJECT"] = "auto-recruiter"

# Setup path imports for question-maker-agent monorepo structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from langsmith import Client, evaluate
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from apps.agents.shared.clients import gemini_flash_lite, gemini_flash
retriever_prompt_module = importlib.import_module("question-maker-agent.prompts.retriever_prompt")
RETRIEVER_SYSTEM_INSTRUCTION = retriever_prompt_module.RETRIEVER_SYSTEM_INSTRUCTION
FORCED_GENERATION_SYSTEM_INSTRUCTION = retriever_prompt_module.FORCED_GENERATION_SYSTEM_INSTRUCTION

API_KEYS = [
    os.getenv("GEMINI_API_KEY1") or os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY2"),
    os.getenv("GEMINI_API_KEY3")
]
API_KEYS = [k for k in API_KEYS if k]
CURRENT_KEY_IDX = 0

def rotate_api_keys(retriever_module=None):
    global CURRENT_KEY_IDX
    global gemini_flash_lite
    
    if len(API_KEYS) <= 1:
        return
        
    CURRENT_KEY_IDX = (CURRENT_KEY_IDX + 1) % len(API_KEYS)
    new_key = API_KEYS[CURRENT_KEY_IDX]
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    new_client = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=new_key,
        temperature=0.0,
        max_retries=0,
        timeout=60.0
    )
    
    # Hot-swap the client globally for this script and the target module
    gemini_flash_lite = new_client
    if retriever_module:
        retriever_module.gemini_flash_lite = new_client
        
    sys.stderr.write(f"\n[!] Rate limit hit. Rotated to API key {CURRENT_KEY_IDX + 1}/{len(API_KEYS)}\n")

FORCED_GENERATION_SYSTEM_INSTRUCTION = retriever_prompt_module.FORCED_GENERATION_SYSTEM_INSTRUCTION

retriever_node_module = importlib.import_module("question-maker-agent.nodes.retriever")
FinalGroundingTheory = retriever_node_module.FinalGroundingTheory
tavily_tool = retriever_node_module.tavily_tool
# Dynamically import because of dash in name
eval_prompts_module = importlib.import_module("question-maker-agent.prompts.retriever_eval_prompt")
RETRIEVER_EVAL_SYSTEM_INSTRUCTION = eval_prompts_module.RETRIEVER_EVAL_SYSTEM_INSTRUCTION
RETRIEVER_EVAL_USER_TEMPLATE = eval_prompts_module.RETRIEVER_EVAL_USER_TEMPLATE

from retriever_test_cases import test_cases

class RetrieverEvaluationResult(BaseModel):
    action_type_score: Literal[0, 1] = Field(description="Score of 1 if action_type was correct, 0 if it was the wrong move.")
    quality_score: float = Field(description="Score from 0 to 5 for the quality dimension.")
    relatedness_score: float = Field(description="Score from 0 to 5 for the relatedness dimension.")
    justification: str = Field(description="Brief explanation of the scores.")

def evaluate_retriever_llm_judge(run, example) -> dict:
    import time
    inputs = example.inputs
    outputs = run.outputs
    
    # ... (skipping some logic here)
    # Actually I should replace the whole function to safely insert the retry loop.
    
    action_type = outputs.get("action_type")
    output_content = outputs.get("output_content")
    
    retrieved_data_str = "None"
    if inputs.get("messages"):
        chunks = []
        for msg in inputs["messages"]:
            if msg["role"] == "assistant":
                queries = [tc["args"].get("query", "") for tc in msg.get("tool_calls", [])]
                chunks.append(f"Queries: {queries}")
            elif msg["role"] == "tool":
                chunks.append(f"Chunk (source: {msg.get('tool_call_id')}): {msg.get('content')}")
        retrieved_data_str = "\n".join(chunks)
        
    user_prompt = RETRIEVER_EVAL_USER_TEMPLATE.format(
        topic=inputs.get("topic"),
        goal=inputs.get("goal"),
        loop_iteration=inputs.get("search_count", 0) + 1,
        retrieved_data=retrieved_data_str,
        action_type=action_type,
        output_content=output_content
    )
    
    messages = [
        SystemMessage(content=RETRIEVER_EVAL_SYSTEM_INSTRUCTION),
        HumanMessage(content=user_prompt)
    ]
    
    import time
    for attempt in range(5):
        try:
            time.sleep(1) # Fast pacing since we have 3 keys
            structured_judge = gemini_flash_lite.with_structured_output(RetrieverEvaluationResult)
            eval_result = structured_judge.invoke(messages)
            return {
                "results": [
                    {"key": "action_type_score", "score": float(eval_result.action_type_score)},
                    {"key": "quality_score", "score": float(eval_result.quality_score)},
                    {"key": "relatedness_score", "score": float(eval_result.relatedness_score)}
                ]
            }
        except Exception as e:
            sys.stderr.write(f"LLM Judge call failed on attempt {attempt}: {e}\n")
            if attempt == 4:
                return {
                    "results": [
                        {"key": "action_type_score", "score": 0.0},
                        {"key": "quality_score", "score": 0.0},
                        {"key": "relatedness_score", "score": 0.0},
                        {"key": "judge_failed", "score": 1.0}
                    ]
                }
            rotate_api_keys()

import time
def evaluate_retriever_target(inputs: dict) -> dict:
    search_count = inputs.get("search_count", 0)
    
    retriever_module = importlib.import_module("question-maker-agent.nodes.retriever")
    state_module = importlib.import_module("question-maker-agent.state")
    InterviewGoal = state_module.InterviewGoal
    
    goal = InterviewGoal(
        goal_id="test_id",
        topic=inputs["topic"],
        goal=inputs["goal"],
        interview_time_in_minute=15,
        need_grounding=True
    )
    
    langchain_messages = []
    for msg in inputs.get("messages", []):
        if msg["role"] == "assistant":
            tcs = []
            for tc in msg.get("tool_calls", []):
                tcs.append({
                    "id": tc["id"],
                    "name": tc["name"],
                    "args": tc["args"]
                })
            langchain_messages.append(AIMessage(content=msg.get("content", ""), tool_calls=tcs))
        elif msg["role"] == "tool":
            langchain_messages.append(ToolMessage(
                tool_call_id=msg["tool_call_id"],
                name=msg["name"],
                content=msg["content"]
            ))
            
    state = {
        "goal": goal,
        "search_count": search_count,
        "messages": langchain_messages,
        "grounding_theories": []
    }
    
    import time
    for attempt in range(5):
        try:
            time.sleep(1)
            output = retriever_module.brain_node(state)
            response = output["messages"][0]
            
            action_type = "tool_call"
            output_content = ""
            
            if hasattr(response, "tool_calls") and response.tool_calls:
                for tc in response.tool_calls:
                    if tc["name"] == "FinalGroundingTheory":
                        action_type = "generate_grounding"
                        output_content = f"GENERATE_GROUNDING:\ntheory: {tc['args'].get('theory')}\nreferences: {tc['args'].get('references')}"
                        break
                
                if action_type == "tool_call":
                    queries = []
                    for tc in response.tool_calls:
                        if tc["name"] == "tavily_search_results_json":
                            queries.append(tc["args"].get("query", ""))
                    output_content = f'TOOL CALL: web_search\nARGS: {{"queries": {queries}}}'
            else:
                action_type = "generate_grounding"
                output_content = response.content
                
            return {
                "action_type": action_type,
                "output_content": output_content
            }
        except Exception as e:
            sys.stderr.write(f"Target call failed on attempt {attempt}: {e}\n")
            if attempt == 4:
                return {
                    "action_type": "error",
                    "output_content": str(e)
                }
            rotate_api_keys(retriever_module)

def main():
    dataset_name = "Retriever Prompt Evaluation"
    client = Client()
    
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception:
        dataset = client.create_dataset(dataset_name=dataset_name)
        
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    # We always upload our dataset if it's new
    if not existing_examples and test_cases:
        print(f"Uploading {len(test_cases)} examples...")
        for example in test_cases:
            client.create_example(
                inputs=example["inputs"],
                dataset_id=dataset.id
            )
            
    print("Evaluating...")
    results = evaluate(
        evaluate_retriever_target,
        data=dataset_name,
        evaluators=[evaluate_retriever_llm_judge],
        experiment_prefix="retriever-run",
        max_concurrency=1
    )

if __name__ == "__main__":
    main()
