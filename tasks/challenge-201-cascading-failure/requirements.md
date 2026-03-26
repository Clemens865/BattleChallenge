# Challenge 201: Recovery From Cascading Failure

## Objective

The test suite for this Python library API project is failing. Your job is to find and fix the **root cause**.

## Input

`input/project/` contains a 12-file Python project implementing a simple book library API. The project has its own test suite in `input/project/tests/`.

## Current Error

Running the tests produces errors like:

```
FAILED tests/test_api.py::test_list_books - AttributeError: 'str' object has no attribute 'isoformat'
FAILED tests/test_api.py::test_get_book - AttributeError: 'str' object has no attribute 'isoformat'
FAILED tests/test_api.py::test_create_book - TypeError: expected date, got str
FAILED tests/test_models.py::test_serialize_book - AttributeError: 'str' object has no attribute 'isoformat'
```

The traceback points to `api_handlers.py` line 45 — but that may NOT be the actual root cause.

## Rules

1. **Do NOT modify any test files** (`tests/test_api.py`, `tests/test_models.py`)
2. **Minimize changes** — fix only what is broken
3. **Find the ROOT CAUSE** — do not patch symptoms in the wrong file

## Required Output

Copy the fixed file(s) to the output directory. Only files you have modified should be in the output. The test harness will overlay your fixes on top of the original project and run the full test suite.

## Scoring

**Binary**: ALL verification tests must pass or score is 0. This is a **two-pass** task.
