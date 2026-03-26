# Challenge 206: Environment Setup & Dependency Resolution

## Objective

You are given a Node.js/TypeScript project that is completely broken due to configuration and dependency issues. The source code is correct but the project configuration makes it impossible to build, run, or test. Your job is to diagnose and fix all configuration issues.

## Input

`input/project/` contains a 10-file project:

- `package.json` — has version conflicts and missing configurations
- `tsconfig.json` — has incorrect compiler settings
- `src/index.ts` — application entry point
- `src/server.ts` — Express HTTP server
- `src/database.ts` — database connection module
- `src/routes.ts` — API route definitions
- `tests/server.test.ts` — server tests
- `tests/database.test.ts` — database tests
- `.env.example` — environment variable template (incomplete)
- `README.md` — project documentation

## Known Problems (you must find and fix ALL)

The project has at least 5 configuration problems that prevent it from building and running. The source code itself is NOT broken — only configuration files need to be fixed.

## Required Output

Place all project files in the output directory with fixes applied. Additionally, produce a `FIXES.md` file documenting each problem you found and how you fixed it.

## Rules

1. **Do NOT modify source files** (`src/*.ts`, `tests/*.ts`) — only fix configuration
2. **Do NOT modify README.md** — leave documentation as-is
3. **Fix only configuration files**: `package.json`, `tsconfig.json`, `.env.example`
4. **All original files must be present** in the output

## Scoring

**Binary**: ALL verification tests must pass or score is 0. This tests the framework's ability to diagnose configuration issues and fix them consistently.
