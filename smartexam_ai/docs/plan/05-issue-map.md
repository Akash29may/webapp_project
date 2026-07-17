# SmartExam AI — Issue → Milestone Map

Board: `Akash29may/webapp_project`. Every build issue mapped to a milestone
(`04-timeline.md`) and plan doc. Status as read from the API on 2026-07-15.

## Build issues

| # | Title (short) | Milestone | Doc | Board status |
|---|---------------|-----------|-----|--------------|
| 39 | Django workspace/settings/routing | M0 | 02 | closed |
| 59 | Init core Django workspace/routing | M0 | 02 | closed |
| 58 | Frontend asset pipeline (Tailwind) | M0/M6 | 03 | closed |
| 48 | PostgreSQL connectivity config | M0 | 01 | open |
| 55 | `.env` for DB + AI keys | M0/M7 | 02 | open |
| 49 | Custom User models (Teacher/Student) | M1 | 01 | open |
| 50 | Course & Module relational models | M1 | 01 | open |
| 51 | Exam Configuration models | M1 | 01 | open |
| 52 | Student progress/session tracking models | M1 | 01 | open |
| 23 | Entity Relationship Diagram (ERD) | M1/DOC | 01 | open |
| 26 | Database Design | M1/DOC | 01 | open |
| 40 | Auth views/registration/tokens | M2 | 02 | open |
| 41 | Role-based middleware/permission walls | M2 | 02 | open |
| 42 | Course Builder engine | M3 | 02 | open |
| 44 | LLM/NLP API client wrapper | M4 | 02 | open |
| 45 | Prompt templates (MCQ & subjective gen) | M4 | 02 | open |
| 46 | AI subjective scoring | M4 | 02 | open |
| 47 | Gap-analysis / study suggestions | M4 | 02 | open |
| 43 | Server-side timer + auto-submit | M5 | 02/03 | open |
| 35 | Exam Session interface | M5 | 03 | open |
| 36 | Anti-cheat JS (tab/blur) | M5 | 03 | open |
| 37 | Client security (copy/paste/right-click) | M5 | 03 | open |
| 32 | Base Django HTML templates | M6 | 03 | closed* |
| 33 | Teacher Dashboard | M6 | 03 | open |
| 34 | Student Dashboard | M6 | 03 | open |
| 38 | Chart.js analytics graphs | M6 | 03 | open |
| 53 | Dockerfile (Django) | M7 | — | open |
| 54 | docker-compose (Django + Postgres) | M7 | — | open |
| 56 | Gunicorn/Nginx production setup | M7 | — | open |

\* #32 marked closed on the board, but no templates exist on disk — treat as
re-create in M6. Confirm with the team.

## Epics (tracking containers, not tasks)

| # | Title | Covered by |
|---|-------|-----------|
| 28 | Frontend | M6 (+M5 runner) |
| 29 | Backend | M2–M5 |
| 30 | Database (PostgreSQL) | M0–M1 |
| 31 | Docker Infrastructure | M7 |
| 27 | API Design | DOC (from 02) |
| 24 | System Design | DOC |
| 25 | TDD Documentation | DOC |

## Documentation issues (DOC track, #1–#22)

| # | Title | Status |
|---|-------|--------|
| 1 | Project Idea & Business Analysis | open |
| 2 | PRD Document | open |
| 3 | SRS Document | open |
| 4 | TDD Document | open |
| 5 | Merging documents in main | closed |
| 6 | Documentation folder hierarchy | closed |
| 7 | Project Overview Document | closed |
| 8 | Problem Statement Document | closed |
| 9 | Stakeholder Analysis | open |
| 10 | Information Gathering | open |
| 11 | Surveys | open |
| 12 | Interviews | open |
| 13 | PRD Documentation | open |
| 14 | User Personas | open |
| 15 | User Journey | open |
| 16 | User Stories | open |
| 17 | Acceptance Criteria | open |
| 18 | Functional Requirements | open |
| 19 | Non-Functional Requirements | open |
| 20 | Use Cases | open |
| 21 | Data Flow Diagram (DFD) | open |
| 22 | SRS Documentation | open |

## Notes / conflicts to confirm with the team
- **Frontend stack:** board = Django templates (#32–35, #38 Chart.js). This plan
  follows that. (Earlier React/DRF draft is superseded.)
- **LLM provider:** #44 says "OpenAI or LangChain"; plan uses a provider-agnostic
  client defaulting to Claude. Confirm which provider is billed.
- **#32 status mismatch:** closed on board but no templates on disk.
