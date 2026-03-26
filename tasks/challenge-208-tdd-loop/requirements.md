# Challenge 208: Test-Driven Development Loop

## Objective

Implement a `date_parser.py` module that makes ALL 25 provided tests pass. You are given ONLY a test file — no implementation.

## Input

- `input/test_date_parser.py` — 25 test cases, ALL currently failing (no implementation exists)

The tests exercise a `parse_date(text: str) -> datetime` function that must handle:

- **ISO 8601**: `"2026-03-26"`, `"2026-03-26T14:30:00"`, `"2026-03-26T14:30:00Z"`, `"2026-03-26T14:30:00+02:00"`
- **Relative dates**: `"today"`, `"yesterday"`, `"tomorrow"`, `"3 days ago"`, `"next week"`, `"last month"`
- **Natural language**: `"March 26, 2026"`, `"26 Mar 2026"`, `"03/26/2026"`, `"26.03.2026"`
- **Edge cases**: Leap year `"2024-02-29"`, end of month `"2026-01-31"`, invalid `"2026-02-30"` (should raise `ValueError`)
- **Timezone handling**: `"2026-03-26T12:00:00-05:00"` should return a timezone-aware datetime

## Rules

1. **Do NOT modify the test file** — implement only `date_parser.py`
2. **Work incrementally** — run tests after each change, fix failures one by one
3. **Use only the Python standard library** — no external packages (no `dateutil`, no `arrow`)

## Required Output

Place `date_parser.py` in the output directory. It must export a `parse_date(text: str) -> datetime` function.

## Scoring

**Binary**: ALL 25 verification tests must pass or score is 0. This is a **two-pass** task — the framework should run tests and iterate.

The key insight: this task rewards frameworks that can execute tests, read failures, and iterate. A single-shot approach will likely miss edge cases.
