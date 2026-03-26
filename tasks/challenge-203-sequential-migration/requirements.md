# Challenge 203: Multi-Step Sequential Migration

## Objective

Rename the `tasks` table to `tickets` and the `task_id` column to `ticket_id` across a database schema with foreign key dependencies.

## Input

- `input/schema.sql` — database schema with 6 tables that have FK dependencies
- `input/seed_data.sql` — 50 rows of test data

### Dependency Graph
```
users -> teams (user belongs to team)
projects -> teams (project belongs to team)
tasks -> projects, users (task belongs to project, assigned to user)
comments -> tasks, users (comment on task by user)
attachments -> comments (attachment to comment)
audit_log -> users (log entry by user)
```

## Required Output

Generate these 5 files in the output directory:

1. **`migration_up.sql`** — Forward migration that renames `tasks` to `tickets` and `task_id` to `ticket_id`. Must drop and recreate foreign keys in correct dependency order.
2. **`migration_down.sql`** — Rollback migration that reverses the rename. Must be in reverse dependency order.
3. **`updated_schema.sql`** — The complete schema after migration (copy of original with all renames applied).
4. **`data_migration.sql`** — SQL statements to update seed data references (column renames in INSERT statements).
5. **`verify_migration.py`** — A Python script that:
   - Connects to a SQLite database
   - Applies the migration
   - Verifies all tables exist with correct names
   - Verifies all foreign keys are intact
   - Returns exit code 0 on success, 1 on failure

## Critical Constraints

- Migration order MUST respect foreign key dependencies
  - Forward: drop FKs from dependents first (attachments, comments), then rename, then recreate FKs
  - Rollback: exact reverse of forward
- All references to `tasks` and `task_id` must be updated everywhere
- The `updated_schema.sql` must be a complete, valid schema (not a diff)
- All SQL must be valid SQLite syntax
- The verify script must be self-contained (no external dependencies beyond Python stdlib + sqlite3)

## Scoring

**Binary**: ALL verification tests must pass or score is 0. Two-pass task.
