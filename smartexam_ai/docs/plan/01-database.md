# SmartExam AI — Database / Models

Aligned to board issues #49, #50, #51, #52, #48, #30, #26 (Database Design),
#23 (ERD). PostgreSQL in dev+prod (SQLite only for the first hours if needed).

## Apps

- `core` — `User` (exists).
- `teachers` — `Teacher` profile (EMPTY — write in M0/M1). — #49
- `students` — `Student` profile (EMPTY — write). — #49
- `courses` — **new** — Course, Module, Resource. — #50, #42
- `exams` — **new** — Exam, Question, Choice, ExamAttempt, Answer. — #51, #52
- `ai` — **new** — no models required beyond `AIEvaluationLog`. — #46, #47, #52

## core.User  (exists — keep)
```
username, password, email, first_name, last_name   (AbstractUser)
is_teacher bool / is_student bool
contact_no char(15) opt / profile_img image opt / bio text opt
```

## teachers.Teacher  (#49 — WRITE)
```
user        OneToOne(User, CASCADE, related_name='teacher')
department  char(100)
designation char(100) opt
```

## students.Student  (#49 — WRITE)
```
user        OneToOne(User, CASCADE, related_name='student')
university  char(255)
department  char(100)
```

## courses.Course  (#50)
```
teacher     FK(Teacher, CASCADE, related_name='courses')
title       char(200)
description text opt
created_at  datetime auto_now_add
```

## courses.Module  (#50 — hierarchy of learning nodes)
```
course      FK(Course, CASCADE, related_name='modules')
title       char(200)
order       PositiveInteger default 0
```

## courses.Resource  (#42 — Course Builder ingest: text files / materials)
```
module      FK(Module, CASCADE, related_name='resources')
title       char(200)
file        FileField(upload_to='resources/') opt
text_body   text opt          # extracted/pasted text used as AI context
order       PositiveInteger default 0
```

## exams.Exam  (#51)
```
course       FK(Course, SET_NULL, null=True, related_name='exams')   # optional link
teacher      FK(Teacher, CASCADE, related_name='exams')
title        char(200)
duration_min PositiveInteger                # timer length  (#43)
is_published bool default False
created_at   datetime auto_now_add
```

## exams.Question  (#51 — MCQ + subjective; difficulty weights)
```
exam         FK(Exam, CASCADE, related_name='questions')
qtype        char choices: 'mcq' | 'subjective'
text         text
marks        PositiveInteger default 1
difficulty   char choices: 'easy'|'medium'|'hard'  default 'medium'   # weight rules
model_answer text opt        # reference answer for subjective AI scoring (#46)
order        PositiveInteger default 0
```

## exams.Choice  (#51 — MCQ options; unused for subjective)
```
question     FK(Question, CASCADE, related_name='choices')
text         char(500)
is_correct   bool default False
```
Serializer rule: MCQ → exactly 4 choices, exactly 1 correct. Subjective → 0.

## exams.ExamAttempt  (#52 — session tracking)
```
exam           FK(Exam, CASCADE, related_name='attempts')
student        FK(Student, CASCADE, related_name='attempts')
started_at     datetime auto_now_add
submitted_at   datetime null=True           # null = in progress
score          Decimal null=True            # total after grading
status         char: 'in_progress'|'submitted'|'auto_submitted'
focus_warnings PositiveInteger default 0     # anti-cheat blur count (#36)
Meta: unique_together (exam, student)
```

## exams.Answer  (#52 — raw responses)
```
attempt         FK(ExamAttempt, CASCADE, related_name='answers')
question        FK(Question, CASCADE)
selected_choice FK(Choice, SET_NULL, null=True)   # MCQ answer
text_response   text opt                           # subjective answer
awarded_marks   Decimal null=True                  # filled at grading
Meta: unique_together (attempt, question)
```

## ai.AIEvaluationLog  (#46, #47, #52 — audit AI scoring & suggestions)
```
attempt        FK(ExamAttempt, CASCADE, related_name='ai_logs')
answer         FK(Answer, CASCADE, null=True)      # null for gap-analysis logs
kind           char: 'subjective_score' | 'gap_analysis' | 'generation'
provider       char(50)          # e.g. 'anthropic'
model          char(100)
prompt         text
response       text
score          Decimal null=True
created_at     datetime auto_now_add
```

## ER (plain text)  — #23 ERD

```
User 1—1 Teacher 1—* Course 1—* Module 1—* Resource
Teacher 1—* Exam 1—* Question 1—* Choice
Course 0—* Exam
User 1—1 Student 1—* ExamAttempt *—1 Exam
ExamAttempt 1—* Answer *—1 Question ; Answer *—0..1 Choice
ExamAttempt 1—* AIEvaluationLog ; Answer 1—* AIEvaluationLog
```

## Grading logic

- **MCQ** (instant, on submit): `awarded = marks if selected_choice.is_correct`.
- **Subjective** (#46, async or on submit): AI compares `text_response` vs
  `model_answer` → semantic score 0..marks; write `awarded_marks` + log.
- `ExamAttempt.score = sum(awarded_marks)`. Timer/deadline enforced server-side
  (#43): past deadline → `status='auto_submitted'`, grade what's saved.
- **Gap analysis** (#47): after grading, aggregate wrong/weak answers by
  module/difficulty → produce study suggestions; store as gap-analysis log.

## PostgreSQL  (#48, #54)
- `DATABASES` reads `DB_ENGINE/NAME/USER/PASSWORD/HOST/PORT` from env.
- Dev may start on SQLite; switch to Postgres before M7. Schema is identical.
