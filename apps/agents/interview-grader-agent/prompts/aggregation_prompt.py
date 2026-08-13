"""
What: LLM prompt template for generating the final reasoning paragraph in the Aggregation node.
Why: Converts raw scores, citations, communication traits, and red flags into a coherent, plain-language explanation of the candidate's performance.
"""

from langchain_core.prompts import ChatPromptTemplate

# System prompt outlining the role and required output format
SYSTEM_PROMPT = """You are an expert technical recruiter and interviewer. 
Your task is to synthesize the results of a technical interview into a concise, plain-language 'reasoning' paragraph.
Explain *why* the candidate received their specific recommendation, rather than just restating the scores.

Use the provided Core Analysis, Communication Traits, and Injection Findings (if any).

Rules:
1. Write a single, cohesive paragraph (no bullet points, no markdown formatting).
2. Focus on the 'why'.
3. If there are red flags (injection attempts) or failing gating criteria, address them as the primary reason for a No-Hire or Hold.
4. Keep it concise, objective, and professional.
5. Return ONLY the paragraph string. Do not include introductory text like 'Here is the reasoning:'.
"""

# User prompt containing the injected payload
USER_PROMPT = """
Recommendation Assigned: {recommendation}
Composite Score: {composite_score}/10
Overall Confidence: {overall_confidence}

--- CORE ANALYSIS ---
{core_summary}

--- COMMUNICATION ---
{communication_summary}

--- RED FLAGS ---
{red_flags_summary}
"""

def get_aggregation_prompt() -> ChatPromptTemplate:
    """Returns the chat prompt template for the final reasoning generation."""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT)
    ])
