# Evals Subdirectory Manifest

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `schemas.py` | Pydantic data structures for GoldFacts, assertions, and LLM Judge scorecard output | `GoldFacts`, `GoldGoalAssertion`, `JudgeReportOutput`, `DeterministicCheckResult` |
| `deterministic.py` | Fast, code-based verification for schema validity, enums, score ranges, and protected character leakage | `run_deterministic_checks`, `check_protected_characteristic_leakage` |
| `prompts/judge_prompt.py` | System and user prompt templates for reference-based LLM judgment | `JUDGE_SYSTEM_PROMPT`, `JUDGE_USER_PROMPT` |
| `judge.py` | Invokes `gemini_flash_lite` to perform qualitative reference-based evaluation | `evaluate_with_llm_judge` |
| `cases/case_01_goroutine_and_db.py` | Mock test case 1 with multi-goal interview transcript and gold assertions | `MOCK_STATE_01`, `GOLD_FACTS_01` |
| `run_evals.py` | CLI test runner that executes core analysis, runs checks, and outputs evaluation report | `main` |
