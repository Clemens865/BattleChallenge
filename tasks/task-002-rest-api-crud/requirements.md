# Task: REST API with CRUD Operations

## Requirements

Build a Python REST API using Flask (or any stdlib-compatible approach) that manages a "todos" resource.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /todos | List all todos |
| POST | /todos | Create a new todo |
| GET | /todos/:id | Get a single todo |
| PUT | /todos/:id | Update a todo |
| DELETE | /todos/:id | Delete a todo |

### Todo Schema

```json
{
  "id": "integer (auto-generated)",
  "title": "string (required)",
  "completed": "boolean (default: false)",
  "created_at": "ISO8601 datetime"
}
```

### Behavior

- POST /todos with `{"title": "Buy milk"}` returns 201 with the created todo
- GET /todos returns 200 with an array of all todos
- GET /todos/:id returns 200 with the todo, or 404 if not found
- PUT /todos/:id with `{"title": "...", "completed": true}` returns 200, or 404
- DELETE /todos/:id returns 204, or 404 if not found
- All responses are JSON

### Constraints

- In-memory storage (no database required)
- Must run on port 5000
- Entry point: `python app.py`

## Acceptance Criteria

- All CRUD operations work correctly
- Proper HTTP status codes
- JSON request/response handling
- Handles missing resources with 404
