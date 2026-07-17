"""Provider-agnostic LLM client.

Isolate all model calls here so the provider is swappable (board issue #44:
"OpenAI or LangChain"). Default provider is Claude (Anthropic). A deterministic
`mock` provider is used for local dev and tests so no network/API key is needed.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from django.conf import settings


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str


class LLMError(Exception):
    """Raised when the provider fails or returns unusable output."""


def _extract_json(text: str):
    """Best-effort: parse a JSON object/array out of a model response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise LLMError(f"Model returned invalid JSON: {exc}") from exc
    raise LLMError("Model response contained no JSON.")


class LLMClient:
    def __init__(self, provider: str | None = None, model: str | None = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL

    # -- public API --------------------------------------------------------
    def complete_json(self, prompt: str, system: str = "", schema: dict | None = None):
        """Return parsed JSON from the model for `prompt`."""
        if self.provider == "mock":
            return _extract_json(self._mock(prompt))
        if self.provider == "anthropic":
            return _extract_json(self._anthropic(prompt, system, schema))
        raise LLMError(f"Unsupported LLM provider: {self.provider}")

    # -- providers ---------------------------------------------------------
    def _anthropic(self, prompt: str, system: str, schema: dict | None) -> str:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise LLMError("anthropic SDK not installed.") from exc

        if not settings.ANTHROPIC_API_KEY:
            raise LLMError("ANTHROPIC_API_KEY is not configured.")

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        kwargs = {
            "model": self.model,
            "max_tokens": 8000,
            "system": system or "You are a helpful assistant that returns strict JSON.",
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema is not None:
            kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
        try:
            response = client.messages.create(**kwargs)
        except Exception as exc:  # noqa: BLE001 - surface provider errors uniformly
            raise LLMError(f"Anthropic request failed: {exc}") from exc

        parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
        if not parts:
            raise LLMError("Anthropic returned no text content.")
        return "".join(parts)

    def _mock(self, prompt: str) -> str:
        """Deterministic offline output keyed to the prompt intent."""
        if "SUBJECTIVE_SCORE" in prompt:
            return json.dumps({"score_ratio": 0.8, "rationale": "Mock: mostly correct, minor gaps."})
        if "GAP_ANALYSIS" in prompt:
            return json.dumps(
                {"suggestions": "Mock: review the weaker modules and retry the missed questions."}
            )
        # default: question generation
        count = 3
        m = re.search(r"COUNT=(\d+)", prompt)
        if m:
            count = int(m.group(1))
        questions = []
        for i in range(count):
            questions.append(
                {
                    "qtype": "mcq",
                    "text": f"Mock generated question {i + 1}?",
                    "marks": 1,
                    "difficulty": "medium",
                    "choices": [
                        {"text": f"Option A{i}", "is_correct": True},
                        {"text": f"Option B{i}", "is_correct": False},
                        {"text": f"Option C{i}", "is_correct": False},
                        {"text": f"Option D{i}", "is_correct": False},
                    ],
                }
            )
        return json.dumps({"questions": questions})
