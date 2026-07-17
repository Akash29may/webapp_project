# SmartExam AI — Phased Timeline

Assumes ~1 focused dev. The board is a full project, not a 4-day task; realistic
end-to-end is **~15–18 working days**. A **shippable core** lands at the end of
M5 (~Day 12). Day counts are estimates — compress if more than one dev.

Each milestone ends runnable. Cut order (if behind) is at the bottom.

---

## M0 — Foundation fix · Day 1   (#39, #48, #59, #55)
- [ ] Write `Teacher` + `Student` models → unbreak the repo.
- [ ] Fix `DEBUG` parsing; set up `.env` (SECRET_KEY, DEBUG, DB_*, LLM keys).
- [ ] Add `courses`, `exams`, `ai` apps to `INSTALLED_APPS`.
- [ ] Wire PostgreSQL settings from env (can still run SQLite locally for now).
- [ ] `makemigrations` + `migrate`; superuser.
**DoD:** `runserver` boots; admin loads; migrations clean.

## M1 — Data layer · Days 2–3   (#49,#50,#51,#52,#23,#26,#30)
- [ ] All models from `01-database.md`: profiles, Course/Module/Resource,
      Exam/Question/Choice, ExamAttempt/Answer, AIEvaluationLog.
- [ ] Register everything in Django admin (fast manual data checks).
- [ ] Draft ERD (#23) + Database Design note (#26) into `docs/`.
**DoD:** full schema migrated; can create a course→exam→question in admin.

## M2 — Auth & roles · Days 4–5   (#40, #41)
- [ ] Registration (teacher/student), login routing by role, logout.
- [ ] `@teacher_required` / `@student_required` + ownership querysets.
- [ ] Basic `base.html` + login/register templates to exercise the flow.
**DoD:** both roles register/login; role walls block cross-access.

## M3 — Course Builder · Days 6–7   (#42, #50)
- [ ] Teacher CRUD: Course → Module → Resource (upload/paste text → `text_body`).
- [ ] Exam authoring CRUD: Exam + MCQ/subjective Questions (+validation).
**DoD:** teacher builds a course with modules/resources and a mixed exam.

## M4 — AI services · Days 8–9   (#44, #45, #46, #47)
- [ ] `ai/client.py` provider-agnostic LLM wrapper (Claude default, env-swappable).
- [ ] `#45` generation from Resource text → draft questions (review→save).
- [ ] `#46` subjective scoring on submit → awarded_marks + log.
- [ ] `#47` gap analysis → study suggestions stored + shown.
**DoD:** teacher AI-generates questions; a subjective answer gets AI-scored.

## M5 — Exam engine · Days 10–12   (#43, #35, #36, #37)  ← SHIPPABLE CORE
- [ ] Attempt lifecycle endpoints (start/resume/state/answer/submit/warn).
- [ ] Server timer + auto-submit; answer-key never leaked pre-submit.
- [ ] `runner.html` with Alpine: timer, navigator, autosave, resume.
- [ ] Anti-cheat (blur/tab detection + warnings) + client copy/paste lock.
- [ ] Result screen (MCQ correctness + subjective rationale).
**DoD (MVP):** register → build exam (manual+AI) → student takes it timed with
anti-cheat → MCQ auto + subjective AI graded → both see results. No key leaks.

## M6 — UI & dashboards · Days 13–15   (#32, #33, #34, #38, #28)
- [ ] Polish base templates/nav.
- [ ] Teacher dashboard: courses/exams + results charts (Chart.js).
- [ ] Student dashboard: progress, per-module performance, gap suggestions.
**DoD:** both dashboards render real data with charts.

## M7 — Infra / Deploy · Days 16–18   (#53, #54, #55, #56, #31)
- [ ] Dockerfile (Django), docker-compose (web + PostgreSQL), `.env` wiring.
- [ ] Gunicorn app server + Nginx reverse proxy + static serving.
- [ ] Prod checklist: `DEBUG=False`, `ALLOWED_HOSTS`, collectstatic, migrate.
- [ ] Smoke test full loop on the container stack.
**DoD:** `docker compose up` serves the app on Postgres, full loop works.

## DOC track (parallel, as capacity allows)   (#1–#27)
PRD/SRS/TDD, personas, journeys, stories, acceptance criteria, functional/non-
functional reqs, use cases, DFD, ERD, system design, API design. Do the ones
that unblock build first (ERD #23, DB design #26, API design #27); the rest are
documentation deliverables that can trail the code.

---

## Definition of done (whole project)
Every M0–M7 DoD met; all board build-issues (see `05-issue-map.md`) closed;
full loop runs on the Docker+Postgres stack with no answer-key leakage.

## Cut order if behind (protect the core loop)
1. Gap analysis depth (#47) → simple rule-based suggestions.
2. Anti-cheat/client-security polish (#36/#37) → basic blur count only.
3. Course Builder file ingest (#42) → paste-text only.
4. Dashboard charts (#38) → plain tables.
5. Full Docker/Nginx (#53–56) → single-container / runserver for demo.
**Never cut:** auth+roles, exam authoring, take+grade (MCQ+subjective),
server timer, answer-key security.
