"""AI services: generation (#45), subjective scoring (#46), gap analysis (#47)."""
from __future__ import annotations

from decimal import Decimal

from .client import LLMClient, LLMError
from . import prompts

__all__ = ["LLMError", "generate_questions", "score_subjective", "analyze_gaps"]


def _client() -> LLMClient:
    return LLMClient()


def generate_questions(source_text: str, count: int, qtypes, difficulty: str) -> list[dict]:
    """Return a list of draft question dicts (NOT saved)."""
    count = max(1, min(int(count), 10))  # cap for cost/latency
    client = _client()
    prompt = prompts.generation_prompt(source_text, count, qtypes, difficulty)
    data = client.complete_json(prompt, prompts.GENERATION_SYSTEM, prompts.GENERATION_SCHEMA)
    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list) or not questions:
        raise LLMError("Generation returned no questions.")
    return questions


def score_subjective(question_text: str, model_answer: str, student_answer: str, marks: int):
    """Return (awarded_marks: Decimal, rationale: str, raw_response: dict)."""
    client = _client()
    prompt = prompts.subjective_prompt(question_text, model_answer or "", student_answer or "", marks)
    data = client.complete_json(prompt, "", prompts.SUBJECTIVE_SCHEMA)
    ratio = data.get("score_ratio", 0) if isinstance(data, dict) else 0
    try:
        ratio = float(ratio)
    except (TypeError, ValueError):
        ratio = 0.0
    ratio = max(0.0, min(ratio, 1.0))
    awarded = (Decimal(str(ratio)) * Decimal(marks)).quantize(Decimal("0.01"))
    rationale = data.get("rationale", "") if isinstance(data, dict) else ""
    return awarded, rationale, data


def analyze_gaps(summary: str) -> str:
    """Return study suggestions text."""
    client = _client()
    prompt = prompts.gap_prompt(summary)
    data = client.complete_json(prompt, "", prompts.GAP_SCHEMA)
    return data.get("suggestions", "") if isinstance(data, dict) else ""
