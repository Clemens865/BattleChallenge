# Task: Todo List CLI Application

## Requirements

Create a Python module `todo.py` that implements a command-line todo list manager. The module must also export a `TodoManager` class that can be used programmatically.

### `TodoManager` Class

```python
class TodoManager:
    def __init__(self, storage_path: str):
        """Initialize with a path to a JSON file for persistence."""

    def add(self, title: str, priority: str = "medium") -> dict:
        """Add a new todo. Returns the created todo dict.
        Priority must be 'low', 'medium', or 'high'.
        Each todo has: id (int), title (str), priority (str), done (bool), created_at (str ISO format)."""

    def list_todos(self, show_done: bool = False) -> list[dict]:
        """Return all todos. If show_done is False, only return incomplete todos."""

    def complete(self, todo_id: int) -> dict:
        """Mark a todo as done. Returns the updated todo. Raises ValueError if not found."""

    def delete(self, todo_id: int) -> dict:
        """Delete a todo by id. Returns the deleted todo. Raises ValueError if not found."""

    def search(self, query: str) -> list[dict]:
        """Search todos by title substring (case-insensitive). Returns matching todos."""
```

### Persistence

- Data is stored in a JSON file at `storage_path`
- Data must survive across multiple `TodoManager` instances using the same file
- IDs are auto-incrementing integers starting at 1

### CLI Interface (via `__main__`)

When run as `python todo.py <command> [args]`, support:
- `add <title> [--priority high|medium|low]`
- `list [--all]`
- `done <id>`
- `delete <id>`
- `search <query>`

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- No external dependencies (stdlib only)
