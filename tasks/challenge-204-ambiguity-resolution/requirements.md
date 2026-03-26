# Challenge 204: Specification Ambiguity Resolution

## Objective

You are given an existing Flask application with users and posts, along with a deliberately vague product requirements document for a new "notification system" feature. Your task is to interpret the ambiguous requirements, make reasonable design decisions, and produce working code that integrates with the existing codebase.

## Input

`input/project/` contains an 8-file Flask application:

- `app.py` — Flask application factory
- `models.py` — User and Post data models
- `routes.py` — API route handlers for users and posts
- `auth.py` — Authentication utilities
- `database.py` — In-memory database layer
- `utils.py` — Shared helper functions
- `config.py` — Application configuration
- `tests/test_routes.py` — Existing test suite

## Product Requirements (Intentionally Vague)

> "Build a notification system for our app. Users should be notified about important events. Notifications should be delivered in a timely manner. The system should be extensible."

No further specification is provided. The following are left undefined:
- Which events trigger notifications
- What delivery channels to use
- What "timely" means
- What "extensible" means architecturally

## Required Output

Place all files in the output directory. You must produce:

1. **The complete existing project** — all 8 original files (unmodified or with minimal integration hooks)
2. **Notification module(s)** — one or more new Python files implementing the notification system
3. **`DECISIONS.md`** — a document explaining every ambiguity you identified and the assumption/decision you made to resolve it

## Scoring

**Binary**: ALL verification tests must pass or score is 0. The framework is tested on its ability to identify ambiguities, make defensible decisions, and produce working, well-structured code.
