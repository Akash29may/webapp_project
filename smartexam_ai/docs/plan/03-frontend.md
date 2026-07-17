# SmartExam AI — Frontend (Django Templates)

Django template-based UI (MVT), Tailwind for styling, **Alpine.js + `fetch`** for
interactivity, **Chart.js** for analytics. No React/SPA. Aligned to #32, #33,
#34, #35, #36, #37, #38, #58, #28.

## Asset pipeline  (#58 — done)

- Tailwind via npm: `input.css` → `static/dist/output.css` (`npm run dev/build`).
- Add Alpine.js and Chart.js as static vendor files (or CDN in dev). Keep them
  local for production CSP simplicity.

## Base templates & layout  (#32)

- `templates/base.html` — html skeleton, Tailwind CSS, nav, `{% block content %}`,
  message flashes, JS includes.
- Partials: `_nav.html`, `_messages.html`, `_footer.html`.
- Two authed shells: teacher nav vs student nav (role-driven).

## Pages / templates

**Auth**
- `registration/register.html` (role toggle: teacher vs student fields),
  `login.html`. (backs #40)

**Teacher**  (#33 Teacher Dashboard)
- `teachers/dashboard.html` — courses, exams, quick stats + Chart.js charts (#38).
- `courses/course_form.html`, `courses/module_form.html`,
  `courses/resource_form.html` — Course Builder UI (#42).
- `exams/exam_form.html` — exam meta + question list.
- `exams/question_form.html` — qtype toggle (MCQ: 4 options+correct radio /
  subjective: model_answer), marks, difficulty.
- `exams/generate.html` (or modal) — topic/count/qtypes → calls generation
  endpoint → renders **draft** questions to accept/edit/save (#45).
- `exams/results.html` — attempts table + score distribution chart (#38).

**Student**  (#34 Student Dashboard)
- `students/dashboard.html` — enrolled courses, published exams, progress +
  performance charts (#38), gap-analysis suggestions (#47).
- `exams/exam_list.html` — published exams, Start button.
- **`exams/runner.html`** — the interactive exam session (#35, below).
- `exams/result.html` — score + per-question review (correct answers /
  subjective AI rationale) after submit.

## Exam runner (the interactive screen)  (#35, #36, #37, #43)

Single template driven by Alpine.js talking to the thin JSON endpoints in
`02-backend.md`.

- **Timer (#43):** initialize from server `seconds_remaining`; tick down client-
  side; re-sync on load; at 0 → auto-submit. Server remains source of truth.
- **Navigator (#35):** grid of question numbers; mark answered/unanswered/flagged.
  One-question view with prev/next.
- **Autosave:** on select/type (debounced) → `POST /attempts/<id>/answer`; show
  "saved" indicator; resume after refresh via `GET /attempts/<id>/state`.
- **Anti-cheat (#36):** `visibilitychange`/`blur` listeners → warning modal +
  `POST /attempts/<id>/warn` to increment `focus_warnings`. Configurable warning
  cap.
- **Client security (#37):** disable copy/paste/right-click/context-menu inside
  the exam wrapper. (Deterrent only — real enforcement is server-side.)
- **Submit:** confirm → `POST submit` → redirect to result.

## Charts  (#38)

- Chart.js on teacher dashboard (score distributions, attempts over time) and
  student dashboard (progress, per-module performance).
- Data delivered via small JSON endpoints or JSON embedded in the template
  context. Keep chart configs in one `static/js/charts.js`.

## Progressive enhancement / resilience

- Core flows (register, login, create exam, submit) work as plain form POSTs;
  JS enhances (autosave, timer). Exam runner needs JS by design.
- Resume-after-refresh handled by server state, not localStorage.

## Explicitly light for now
- No component framework, no build step beyond Tailwind + vendored JS.
- No dark mode/i18n/animations beyond basics.
