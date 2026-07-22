"""Prompt templates for AI services (board issue #45)."""

GENERATION_SYSTEM = (
    "You are an exam author. Generate high-quality exam questions from the "
    "provided source material. Return STRICT JSON only, no prose."
)

GENERATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "qtype": {"type": "string", "enum": ["mcq", "subjective"]},
                    "text": {"type": "string"},
                    "marks": {"type": "integer"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "model_answer": {"type": "string"},
                    "choices": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "text": {"type": "string"},
                                "is_correct": {"type": "boolean"},
                            },
                            "required": ["text", "is_correct"],
                        },
                    },
                },
                "required": ["qtype", "text", "marks", "difficulty"],
            },
        }
    },
    "required": ["questions"],
}

SUBJECTIVE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "score_ratio": {"type": "number"},
        "rationale": {"type": "string"},
    },
    "required": ["score_ratio", "rationale"],
}

GAP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"suggestions": {"type": "string"}},
    "required": ["suggestions"],
}


def generation_prompt(source_text: str, count: int, qtypes, difficulty: str) -> str:
    qtypes_str = ", ".join(qtypes)
    return (
        f"COUNT={count}\n"
        f"Generate exactly {count} exam questions of type(s): {qtypes_str}, "
        f"at {difficulty} difficulty, based ONLY on the source material below.\n"
        "For each MCQ provide exactly 4 choices with exactly one correct. "
        "For each subjective question provide a concise model_answer.\n"
        'Return JSON: {"questions": [{"qtype","text","marks","difficulty",'
        '"model_answer"?,"choices"?:[{"text","is_correct"}]}]}\n\n'
        f"SOURCE MATERIAL:\n{source_text}"
    )


def subjective_prompt(question_text: str, model_answer: str, student_answer: str, marks: int) -> str:
    return (
        "SUBJECTIVE_SCORE\n"
        "Score the student's answer against the model answer for semantic "
        "relevance and correctness.\n"
        f"Question: {question_text}\n"
        f"Model answer: {model_answer}\n"
        f"Student answer: {student_answer}\n"
        f"Max marks: {marks}\n"
        'Return JSON: {"score_ratio": <0..1>, "rationale": "<short>"}'
    )


def gap_prompt(summary: str) -> str:
    return (
        "GAP_ANALYSIS\n"
        "Given this student's per-topic performance, identify weak spots and "
        "produce concise, actionable study suggestions.\n"
        f"Performance summary:\n{summary}\n"
        'Return JSON: {"suggestions": "<text>"}'
    )
