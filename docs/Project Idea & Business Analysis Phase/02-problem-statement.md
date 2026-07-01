# Problem Statement

**Project:** SmartExam AI
**Phase:** Project Idea & Business Analysis
**Status:** Draft

---

## 1. Background

Assessment is central to education, yet the work surrounding it is overwhelmingly manual.
Teachers spend a disproportionate share of their time on administrative tasks — drafting
unique question papers, grading scripts (especially subjective answers), and updating
performance records — rather than on instructional design. At the same time, remote and
flexible learning has become mainstream, but most online assessment tools still treat the
exam as a static, one-size-fits-all artifact and offer learners little beyond a final
grade.

## 2. The Core Problem

> Educators are burdened by repetitive, time-consuming assessment work, while learners
> lack unique, fair examinations and the personalized, data-driven feedback needed to
> improve.

This single problem has two faces — one for each primary stakeholder.

## 3. Problem Breakdown

### 3.1 Teacher-Side Problems

| ID   | Problem                                                                                       | Impact                                              |
|------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------|
| P-T1 | Manually writing original questions for every exam is slow and repetitive.                    | Lost instructional time; questions get reused/leaked.|
| P-T2 | Grading subjective, long-form answers is labor-intensive and inconsistent between markers.    | Delays, fatigue, and grading bias.                  |
| P-T3 | Maintaining and updating student performance records by hand is error-prone.                  | Inaccurate records; no timely insight.              |
| P-T4 | Reusing question banks across cohorts causes question leakage and weakens academic integrity. | Compromised assessment validity.                    |

### 3.2 Student-Side Problems

| ID   | Problem                                                                            | Impact                                          |
|------|-----------------------------------------------------------------------------------|-------------------------------------------------|
| P-S1 | Geographic and transit constraints limit access to quality assessment.            | Reduced access and flexibility.                 |
| P-S2 | Feedback is usually a single grade with no explanation of *why* or *what next*.    | Students cannot target their weak areas.        |
| P-S3 | Inconsistent grading of subjective answers feels unfair and demotivating.         | Lower trust and engagement.                     |
| P-S4 | No clear, visual view of progress over time.                                      | Hard to measure growth or stay motivated.       |

### 3.3 Integrity Problems (Remote Context)

| ID   | Problem                                                                         | Impact                                  |
|------|---------------------------------------------------------------------------------|-----------------------------------------|
| P-I1 | Remote exams are easy to game by switching tabs or copying questions/answers.   | Compromised fairness.                   |
| P-I2 | Without a server-authoritative timer, clients can manipulate exam duration.     | Unequal exam conditions.                |

## 4. Consequences of Inaction

If these problems are left unaddressed:

- Teachers continue to spend hours on tasks that could be automated, reducing time for
  actual teaching.
- Assessment quality and integrity degrade as question banks are reused.
- Students receive opaque grades and disengage from the learning loop.
- Institutions cannot scale high-quality, fair assessment to remote learners.

## 5. Proposed Solution (Summary)

SmartExam AI addresses the problem by:

1. **Automating question creation** — AI generates unique, context-aware papers from
   course material (addresses P-T1, P-T4).
2. **Automating subjective grading** — an LLM scores long-form answers consistently and
   with rationale (addresses P-T2, P-S3).
3. **Automating record-keeping and analytics** — results flow directly into a progress
   tracker with gap analysis (addresses P-T3, P-S2, P-S4).
4. **Enforcing fair conditions** — a server-side timer and a basic anti-cheat layer
   (addresses P-I1, P-I2, P-S1).

Each solution element maps to a core feature (F1–F6) described in `01-project-overview.md`.

## 6. Problem-to-Feature Traceability

| Problem(s)          | Addressed by Feature                         |
|---------------------|----------------------------------------------|
| P-T1, P-T4          | F2 — AI Question Generator                    |
| P-T2, P-S3          | F5 — AI Subjective Auto-Evaluation            |
| P-T3, P-S2, P-S4    | F6 — Progress Tracker                         |
| P-I1                | F4 — Basic Anti-Cheat Logic                   |
| P-I2                | F3 — Timer-Based Exam                          |
| P-S1                | F1 + F3 — Remote course delivery and exams    |

## 7. Scope Boundary of the Problem

This project tackles the **assessment and feedback loop** for structured courses. It does
*not* attempt to solve content authoring quality, accreditation, or high-stakes proctoring
(which is explicitly deferred to Future Work). The problem is intentionally bounded to what
the six MVP features can credibly deliver.
