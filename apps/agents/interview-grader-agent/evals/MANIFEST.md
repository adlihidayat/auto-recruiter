# Evals Directory Manifest

This directory contains the evaluation and regression testing framework for the `interview-grader-agent`.

| File Name | Purpose | Key Exports/Dependencies |
| --- | --- | --- |
| `schemas.py` | Data contracts for test assertions, deterministic metrics, and LLM Judge reports | `GoldGoalAssertion`, `GoldFacts`, `DeterministicCaseResult`, `LLMJudgeResult`, `EvalCaseReport` |
| `deterministic.py` | Zero-LLM pure Python code assertions (ranges, booleans, enums, guardrails) | `evaluate_deterministic()` |
| `judge.py` | Qualitative reading comprehension judge powered by `gemini_flash_lite` | `evaluate_llm_judge()` |
| `runner.py` | Orchestrates test runs across cases and formats console reporting tables | `run_evaluation_suite()` |
| `prompts/judge_prompt.py` | System and user prompt templates for the LLM Judge | `JUDGE_SYSTEM_PROMPT`, `JUDGE_USER_PROMPT` |
| `cases/core_analysis_cases.py` | Benchmark test cases (01-11) spanning diverse job types and edge cases | `ALL_TEST_CASES` |
