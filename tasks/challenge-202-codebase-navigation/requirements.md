# Challenge 202: Large Codebase Navigation

## Objective

Add rate limiting to the `POST /api/users` endpoint in a 40-file Python monorepo.

## Input

`input/project/` contains a monorepo with 3 packages:
- `packages/core/` — shared utilities, config system, base classes
- `packages/api/` — REST API with routes, middleware, auth
- `packages/worker/` — background job processor

## Requirements

1. **Add rate limiting middleware** that limits `POST /api/users` to a configurable number of requests per minute per client IP
2. **Use the existing config system** in `packages/core/src/config.py` — add a `RATE_LIMIT_REQUESTS_PER_MINUTE` config key with default value `60`
3. **Follow the existing middleware pattern** used by the auth middleware in the API package
4. **Apply rate limiting ONLY to `POST /api/users`** — other endpoints must not be affected
5. Return HTTP 429 with `{"error": "Rate limit exceeded", "retry_after": <seconds>}` when limit is hit

## Required Output

Output all modified and new files, preserving the directory structure. For example, if you modify `packages/api/src/middleware/auth.py`, output it at `packages/api/src/middleware/auth.py` in OUTPUT_DIR.

## Constraints

- No external dependencies — only Python standard library
- Must integrate with the existing codebase patterns
- Do not modify test files
- Minimize changes to existing files

## Scoring

**Binary**: ALL verification tests must pass or score is 0. Two-pass task.
