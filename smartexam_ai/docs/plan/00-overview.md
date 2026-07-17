> **⚠️ ARCHITECTURE UPDATE (implemented):** The refactor was built as a
> **decoupled React (Vite) SPA + Django REST API**, living in `../../refactor/`
> (`frontend/` + `backend/`), per the user's decision. This **supersedes the
> Django-MVT approach** described in the "Architecture" section below and in
> `03-frontend.md`. The data model (`01-database.md`), AI services, exam engine,
> and issue mapping (`05-issue-map.md`) all still apply — only the frontend
> delivery changed (React screens instead of Django templates; DRF JSON
> endpoints instead of template views). See `refactor/README.md` for the
> as-built system.

# SmartExam AI — Build/Refactor Plan (Overview)

> This plan is aligned to the GitHub project board
> (`Akash29may/webapp_project`, issues #1–#68). Every build issue is mapped to a
> milestone in `05-issue-map.md`. Scope = the board, not a reduced MVP — but we
> ship a **working core first** (see the MVP checkpoint), then layer the rest.

## 1. Product (per the board)

An AI-assisted exam platform. Teachers build **courses/modules** and **exams**
(MCQ **and** subjective), optionally AI-generated from course material. Students
take **timed, anti-cheat-guarded** exams; MCQs auto-grade, **subjective answers
are AI-scored**, and a **gap-analysis** engine outputs study suggestions.
Both roles get dashboards with **Chart.js** analytics. Ships on **Docker +
PostgreSQL + Gunicorn/Nginx**.

## 2. Architecture (decided by the board)

| Layer | Choice | Board evidence |
|-------|--------|----------------|
| Backend | Django 6 (modular settings) | #39, #59 (closed) |
| Frontend | **Django templates + Tailwind + light JS** | #32 (closed), #33–35, #58 (closed) |
| Interactivity | Vanilla JS / **Alpine.js**, `fetch` → small JSON views | #35, #36, #37, #43 |
| Charts | **Chart.js** | #38 |
| DB | **PostgreSQL** (SQLite only for very early dev) | #30, #48, #54 |
| AI | Provider-agnostic LLM client (recommend **Claude**) | #44, #45, #46, #47 |
| Infra | **Docker Compose + Gunicorn + Nginx** | #53–#56 |

> **NOTE — reversal from the earlier draft plan:** the earlier draft proposed
> React + DRF. The board contains no React/DRF/Vite issues and the Django
> template base is already closed (#32). This plan follows the board: **Django
> MVT**. Exam-runner richness (timer, autosave, anti-cheat) is delivered with
> Alpine.js + `fetch` against thin Django JSON endpoints — no SPA needed.

## 3. Current repo reality (must fix Day 1)

- `students/models.py` and `teachers/models.py` are **empty** but imported by
  `core/forms.py` → project is currently broken. (Blocks #49.)
- `DEBUG = os.getenv("DEBUG", True)` is always truthy — fix parsing.
- No templates exist on disk despite #32 being marked closed — treat base
  templates as **to (re)create** in Milestone 6, not assume present.
- No `exams`/`courses` apps yet.

## 4. Milestones (each maps to issues — see `05-issue-map.md`)

- **M0 Foundation fix** — unbreak repo, settings, PostgreSQL wiring. (#39,#48,#59)
- **M1 Data layer** — User profiles, Course/Module, Exam config, Attempts/Sessions,
  AI-eval logs. (#49,#50,#51,#52,#30,#26,#23)
- **M2 Auth & roles** — registration, login, role middleware/permission walls.
  (#40,#41)
- **M3 Course Builder** — ingest text/resources, modular sequencing. (#42)
- **M4 AI services** — LLM client, prompt templates (MCQ+subjective generation),
  subjective scoring, gap analysis. (#44,#45,#46,#47)
- **M5 Exam engine** — server-side timer + auto-submit, session interface,
  anti-cheat + client security. (#43,#35,#36,#37)
- **M6 UI & dashboards** — base templates, teacher/student dashboards, Chart.js.
  (#32,#33,#34,#38,#28)
- **M7 Infra/Deploy** — Dockerfile, compose w/ Postgres, `.env`, Gunicorn/Nginx.
  (#53,#54,#55,#56,#31)
- **DOC track (parallel)** — PRD/SRS/TDD/ERD/DFD/API design etc. (#1–#27)

## 5. MVP / "shippable core" checkpoint

End of **M5** = a demoable product: register → teacher builds an MCQ+subjective
exam (manual or AI-generated) → student takes it timed with anti-cheat → MCQ
auto-graded + subjective AI-scored → both see results. Everything after (rich
dashboards polish, full Docker/Nginx, gap-analysis depth) hardens and scales it.

## 6. Docs in this folder

- `00-overview.md` — this file.
- `01-database.md` — full schema (courses, exams, subjective, sessions, AI logs).
- `02-backend.md` — apps, views/endpoints, auth, AI services, exam engine.
- `03-frontend.md` — Django templates, Alpine/JS, exam runner, Chart.js.
- `04-timeline.md` — phased day-by-day plan + definition of done per milestone.
- `05-issue-map.md` — every board issue → milestone → doc + status.
