# SmartExam AI — Backend

Django MVT. Views render templates and also expose a few thin JSON endpoints for
the interactive exam runner / autosave. Session auth (Django default). Aligned to
#39,#40,#41,#42,#43,#44,#45,#46,#47,#48,#27 (API Design).

## Settings & structure  (#39, #59 — done; harden)

- Modular settings `base/local/production` (or one file + env flags to start).
- Fix `DEBUG = os.getenv("DEBUG","True")=="True"`.
- `.env` (#55): `SECRET_KEY, DEBUG, DB_*`, `LLM_PROVIDER`, `ANTHROPIC_API_KEY`.
- `INSTALLED_APPS += courses, exams, ai`.

## Auth & roles  (#40, #41)

- Registration reuses existing `Student/TeacherSignUpForm` logic → creates
  `User` + profile in one transaction, logs in. (#40)
- Login view: authenticate → route to teacher/student dashboard by role.
- **Role enforcement (#41):** custom decorators `@teacher_required` /
  `@student_required` (or mixins for CBVs) that 403/redirect. Apply to every
  teacher- and student-scoped view. Object ownership enforced in querysets
  (`request.user.teacher.exams` — never trust IDs from the client).

## Course Builder  (#42, #50)

- Teacher CRUD for Course → Module → Resource.
- Resource ingest: upload a text file or paste text → store `text_body`
  (extract text server-side). This `text_body` is the **AI context** for
  question generation. Keep extraction simple (txt/plain first; PDF later).

## Exam authoring  (#51)

- Teacher CRUD for Exam, Question (MCQ + subjective), Choice.
- Validation: MCQ = 4 choices/1 correct; subjective = `model_answer` required.
- Publish/unpublish toggle gates student visibility.

## Exam engine (student)  (#43, #35, #52)

Thin JSON endpoints backing the exam-runner template:
```
POST /exams/<id>/attempt         start/resume -> attempt id + seconds_remaining
GET  /attempts/<id>/state        questions (NO is_correct/model_answer) + saved answers + seconds_remaining
POST /attempts/<id>/answer       autosave {question_id, choice_id | text_response}
POST /attempts/<id>/submit       grade -> redirect to result
POST /attempts/<id>/warn         anti-cheat: increment focus_warnings  (#36)
```
- **Server owns the clock (#43):** `seconds_remaining = duration*60 - (now-started)`.
  Submit past deadline → clamp + `auto_submitted`. Client timer is UX only.
- **Answer-key safety:** the take-state serializer must never include
  `is_correct` or `model_answer`. Separate review serializer used only after
  submit.

## AI services  (`ai/services.py`)  (#44–#47)

Isolate all model calls behind one provider-agnostic module so the provider is
swappable (issue #44 says "OpenAI or LangChain"; we recommend Claude).

```
ai/
  client.py     # LLMClient: .complete(prompt, system) -> str ; provider from env
  prompts.py    # templates (#45)
  services.py   # generate_questions / score_subjective / analyze_gaps
```

- **#44 client wrapper:** single `LLMClient`. Default provider = Claude
  (`anthropic` SDK); key from env, server-side only. Provider chosen by
  `LLM_PROVIDER` env so OpenAI/LangChain can be dropped in without touching
  callers. Final model tier picked at implementation (keep the call in one place).
- **#45 generation:** prompt templates take Resource `text_body` + {count, qtypes,
  difficulty} → strict JSON list of questions (MCQ w/ 4 choices+correct, or
  subjective w/ model_answer). Returned as **drafts** for teacher review before
  save — AI stays out of the write path.
- **#46 subjective scoring:** prompt with question + model_answer + student
  `text_response` → JSON {score 0..marks, rationale}. Validate/clamp; write
  `awarded_marks` + `AIEvaluationLog`. Run on submit (or a queued task if slow).
- **#47 gap analysis:** aggregate an attempt's wrong/weak answers by module &
  difficulty → prompt → study-suggestion text; store as gap-analysis log; show
  on student result/dashboard.

Robustness: validate AI JSON shape; on malformed output retry once then surface
a clear error. Never block grading of MCQs on AI failure — subjective can be
marked "pending" and rescored.

## API design doc  (#27)

Document the endpoint list above (auth, courses, exams, attempts, ai) with
request/response shapes in `docs/` as part of the DOC track.

## Permissions summary

- teacher-only: course/module/resource/exam/question CRUD, generation, results.
- student-only: published-exam list, attempt lifecycle, own results.
- ownership via querysets; role via decorators (#41).
