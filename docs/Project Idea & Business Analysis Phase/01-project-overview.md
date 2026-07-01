# Project Overview

**Project Name:** SmartExam AI — An Intelligent Assessment Ecosystem
**Document Version:** 1.0
**Phase:** Project Idea & Business Analysis
**Status:** Draft

---

## 1. Introduction

SmartExam AI is a comprehensive, AI-driven educational ecosystem designed to bridge the
gap between structured learning and automated assessment. It enables teachers to author
modular courses and exam pipelines, and empowers students to take rigorous, time-bound
examinations remotely. The platform uses Generative AI to curate unique examination
papers and to evaluate subjective, long-form responses, producing a high-integrity,
scalable, and personalized academic experience.

This document provides a high-level overview of the project: its vision, objectives,
scope, target users, and the core capabilities that define the Minimum Viable Product
(MVP).

## 2. Vision Statement

> To eliminate the manual administrative burden of assessment and to give every learner a
> personalized, data-driven path to mastery — by combining structured course delivery with
> AI-generated examinations and AI-assisted grading.

## 3. Project Objectives

| ID  | Objective                                                                                 |
|-----|-------------------------------------------------------------------------------------------|
| O1  | Allow teachers to design modular courses and pre-set examination patterns.                |
| O2  | Automatically generate unique, context-aware questions from course material using AI.     |
| O3  | Deliver fair, server-timed examinations with a basic anti-cheat layer.                     |
| O4  | Automatically evaluate subjective answers using an LLM with consistent, explainable scoring.|
| O5  | Provide students with progress analytics and actionable, gap-based study suggestions.      |
| O6  | Keep the AI layer provider-agnostic so the underlying LLM can be swapped without rework.    |

## 4. Scope

### 4.1 In Scope (MVP)

The MVP is defined by six core features:

| Code | Feature                          | Summary                                                                 |
|------|----------------------------------|-------------------------------------------------------------------------|
| F1   | Course Creation                  | Teacher dashboard to build modular outlines and pre-set exam patterns.  |
| F2   | AI Question Generator            | NLP-driven generation of original questions from course notes.          |
| F3   | Timer-Based Exam                 | Server-side synchronized timer with automatic submission on expiry.     |
| F4   | Basic Anti-Cheat Logic           | Tab/blur detection and clipboard (copy/paste) disabling.                |
| F5   | AI Subjective Auto-Evaluation    | LLM grading of long-form answers on semantics, keywords, and depth.     |
| F6   | Progress Tracker                 | Analytics dashboard with growth charts and gap analysis.                |

### 4.2 Out of Scope (Future Work)

- **Advanced Anti-Cheat:** AI proctoring (webcam/mic), gaze tracking, object detection.
- **Adaptive Testing:** difficulty recalibration based on live performance.
- **Safe Exam Browser (SEB) integration:** OS-level lockdown.
- **Voice Analysis:** ambient-audio monitoring for dishonesty indicators.
- **Personalized Learning Path:** proactive module/resource recommendations beyond the MVP gap analysis.

## 5. Target Users (Stakeholders)

| Stakeholder | Role in the System                                                                          |
|-------------|---------------------------------------------------------------------------------------------|
| Teacher     | Primary architect — designs courses, defines exam patterns, reviews AI output and results.  |
| Student     | Primary beneficiary — consumes material, sits exams, and tracks personal progress.          |
| System / AI | Automated actor — generates questions, evaluates answers, enforces timers, logs events.     |
| Administrator (secondary) | Manages accounts and platform configuration; minimal role in the MVP.         |

A detailed breakdown is provided in `03-stakeholder-analysis.md`.

## 6. High-Level Solution Approach

- **Architecture:** A Django (Model–View–Template) web application serving HTML/CSS/JS,
  backed by a PostgreSQL database.
- **AI Layer:** A provider-agnostic **LLM Gateway** exposing a stable internal interface
  (`generate_questions`, `evaluate_answer`). Concrete adapters (Gemini, Claude, OpenAI,
  etc.) are selected by configuration, so no business logic changes when the provider changes.
- **Asynchronous Processing:** Long-running AI tasks (generation, evaluation) run as
  background jobs (Celery + Redis) so the request/response cycle stays responsive.
- **Integrity:** The exam timer is authoritative on the server; the client UI is only a
  mirror. Anti-cheat events are captured client-side and logged server-side.

The technical realization is detailed in the Technical Design Document (TDD) phase
(`18`–`22`).

## 7. Success Criteria

| Metric                                   | Target (MVP)                                                  |
|------------------------------------------|--------------------------------------------------------------|
| Teacher can create a course + exam       | End-to-end in under 15 minutes without assistance.           |
| AI question generation                   | Produces a usable draft paper that a teacher edits, not rewrites.|
| Exam fairness                            | 100% of sessions auto-submit at the server deadline.         |
| Subjective grading consistency           | AI scores are reproducible and accompanied by rationale.     |
| Student insight                          | Each result yields at least one concrete, actionable suggestion.|
| Provider portability                     | Switching LLM provider requires only configuration changes.  |

## 8. Assumptions and Constraints

- **Assumptions:** Users have a stable internet connection and a modern desktop browser;
  course material is supplied by the teacher in text form.
- **Constraints:** MVP targets desktop web; the basic anti-cheat layer is best-effort and
  browser-based (not a substitute for proctoring); AI cost and latency are bounded by
  using asynchronous jobs and provider-agnostic adapters.

## 9. Related Documents

- `02-problem-statement.md` — the problem this project solves.
- `03-stakeholder-analysis.md` — detailed stakeholder breakdown.
- `04-information-gathering.md`, `05-interviews.md`, `06-surveys.md` — requirements research.
- PRD (`08`–`12`), SRS (`13`–`17`), TDD (`18`–`22`) — downstream specification.
