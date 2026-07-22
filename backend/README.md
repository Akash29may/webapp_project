# SmartExam AI — Backend (Django + DRF)

JSON API for the React SPA. Session-cookie auth + CSRF. Provider-agnostic AI
(Claude by default; a deterministic `mock` provider for dev/tests).

## Apps
- `core` — custom `User` + auth endpoints
- `teachers` / `students` — role profiles
- `courses` — Course / Module / Resource (Course Builder)
- `exams` — Exam / Question / Choice / ExamAttempt / Answer + exam engine
- `ai` — LLM client, generation / subjective scoring / gap analysis, `AIEvaluationLog`

## Run (dev)
```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env                 # LLM_PROVIDER=mock works offline
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py createsuperuser
./.venv/bin/python manage.py runserver   # http://localhost:8000
```

## Test
```bash
./.venv/bin/python -m pytest        # 18 tests
```

## Enable real AI
Set in `.env`: `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=sk-...`,
`LLM_MODEL=claude-opus-4-8`. All model calls are isolated in `ai/client.py`
(swap `LLM_PROVIDER` to add OpenAI/LangChain without touching callers).

## API surface
Auth: `/api/auth/{csrf,register,login,logout,me}/`
Teacher: `/api/courses/…`, `/api/modules/…`, `/api/resources/…`,
`/api/exams/…`, `/api/exams/<id>/questions/`, `/api/questions/<id>/`,
`/api/exams/<id>/generate/`, `/api/exams/<id>/results/`
Student: `/api/student/exams/`, `/api/exams/<id>/attempt/`,
`/api/attempts/<id>/`, `/api/attempts/<id>/{answer,submit,warn,result}/`

## Security notes
- Student take-state serializers never include `is_correct` / `model_answer`.
- Object access is scoped by `get_queryset` (teachers → own exams, students →
  own attempts).
- The exam timer is authoritative server-side; late submits are `auto_submitted`.
