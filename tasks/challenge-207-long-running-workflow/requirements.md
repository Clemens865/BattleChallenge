# Challenge 207: Long-Running Workflow Resilience

## Objective

Build a complete REST API from a Product Requirements Document (PRD) and OpenAPI specification. The generated API must conform exactly to the provided OpenAPI 3.0 spec.

## Input

- `input/prd.md` — A detailed PRD describing a complete inventory management REST API
- `input/openapi.yaml` — An OpenAPI 3.0 specification that the generated API must conform to

The API includes:
- 6 endpoints: GET/POST/PUT/DELETE for items, GET for categories, POST for search
- JWT authentication on all endpoints
- SQLite database with 3 tables (items, categories, users)
- Input validation with proper error messages
- Pagination on list endpoints

## Requirements

Build the complete API from the PRD. The API must match the OpenAPI spec exactly. Include:

1. **Models** (`models.py`) — SQLAlchemy or dataclass models for items, categories, users
2. **Routes** (`routes.py`) — All 6 endpoint handlers
3. **Auth** (`auth.py`) — JWT authentication middleware
4. **Database** (`database.py`) — SQLite database setup and connection
5. **Migrations** (`migrations.py`) — Schema creation / migration logic
6. **Seed data** (`seed.py`) — Script to populate initial data
7. **Validation** (`validators.py`) — Input validation logic
8. **App entry** (`app.py`) — Application setup tying everything together

## Key Constraints

- All responses must match the exact JSON shapes defined in the OpenAPI spec
- Error responses must use a consistent format: `{"error": "<message>", "status": <code>}`
- Pagination must use `page` and `limit` query parameters
- JWT tokens must be passed via `Authorization: Bearer <token>` header
- Items must have `created_at` and `updated_at` timestamp fields
- Search endpoint must support filtering by `name`, `category`, and `min_price`/`max_price`

## Scoring

**Binary**: ALL verification tests must pass or score is 0. This is a **two-pass** task — the framework may iterate on its output.
