# SmartExam AI — Refactor (React + Django REST)

The rebuilt SmartExam AI as a **decoupled SPA + API**:

- `backend/` — Django + Django REST Framework JSON API (session-cookie auth).
- `frontend/` — React (Vite) SPA: Tailwind, React Router, TanStack Query, Chart.js.

This is the as-built system that supersedes the Django-MVT plan in
`../smartexam_ai/docs/plan/` (the data model, AI services, exam engine, and
issue mapping in those docs still apply — only the frontend delivery changed).

## What it does
Teachers build courses/modules/resources and exams (MCQ + subjective, optionally
**AI-generated** from resource text). Students take **timed, anti-cheat-guarded**
exams with autosave and resume; MCQs auto-grade instantly, subjective answers are
**AI-scored**, and a **gap-analysis** engine returns study suggestions. Both roles
get dashboards with charts.

## Run it (dev)
Two terminals:

```bash
# 1) backend  → http://localhost:8000
cd backend
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env                       # LLM_PROVIDER=mock → no API key needed
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py createsuperuser
./.venv/bin/python manage.py runserver

# 2) frontend → http://localhost:5173  (Vite proxies /api → :8000)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, register a teacher and a student in separate
browsers/profiles, and run the full loop.

## Test
```bash
cd backend  && ./.venv/bin/python -m pytest   # Django/DRF tests
cd frontend && npm run test                   # Vitest
```

## Real AI (Claude)
In `backend/.env`: `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=sk-...`,
`LLM_MODEL=claude-opus-4-8`. Provider is swappable in `backend/ai/client.py`
(the board's #44 "OpenAI or LangChain" note is satisfied by this abstraction).

## Production (Docker)
`docker compose up --build` brings up PostgreSQL + Gunicorn backend + the built
React SPA served by Nginx (which also reverse-proxies `/api`). See
`docker-compose.yml`, `backend/Dockerfile`, and `frontend/` for details.

## Board issue coverage
Auth+roles (#40/#41), custom user (#49), courses/modules (#50/#42), exam config
(#51), attempts/sessions (#52), server timer + auto-submit (#43), AI client
(#44), generation (#45), subjective scoring (#46), gap analysis (#47), exam
runner + anti-cheat (#35/#36/#37), dashboards + charts (#33/#34/#38), Postgres
+ Docker + Gunicorn (#48/#53/#54/#55/#56). See
`../smartexam_ai/docs/plan/05-issue-map.md`.
