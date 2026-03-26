"""Outcome-based tests for Todo CLI task."""
import importlib.util
import json
import os
import tempfile
import pytest


def load_solution():
    """Load TodoManager from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "todo.py")
    if not os.path.exists(module_path):
        pytest.skip(f"todo.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("todo", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TodoManager


@pytest.fixture
def manager():
    TodoManager = load_solution()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        yield TodoManager(path)
    finally:
        if os.path.exists(path):
            os.unlink(path)


@pytest.fixture
def storage_path():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


# --- Add ---

def test_add_returns_todo(manager):
    todo = manager.add("Buy groceries")
    assert todo["title"] == "Buy groceries"
    assert todo["done"] is False
    assert todo["priority"] == "medium"
    assert "id" in todo

def test_add_with_priority(manager):
    todo = manager.add("Urgent task", priority="high")
    assert todo["priority"] == "high"

def test_add_increments_id(manager):
    t1 = manager.add("First")
    t2 = manager.add("Second")
    assert t2["id"] == t1["id"] + 1

def test_add_has_created_at(manager):
    todo = manager.add("Timestamped")
    assert "created_at" in todo
    assert len(todo["created_at"]) > 0


# --- List ---

def test_list_empty(manager):
    assert manager.list_todos() == []

def test_list_returns_added(manager):
    manager.add("Task A")
    manager.add("Task B")
    todos = manager.list_todos()
    titles = [t["title"] for t in todos]
    assert "Task A" in titles
    assert "Task B" in titles

def test_list_hides_done_by_default(manager):
    manager.add("To do")
    t = manager.add("Will complete")
    manager.complete(t["id"])
    todos = manager.list_todos(show_done=False)
    assert all(not t["done"] for t in todos)

def test_list_show_all(manager):
    manager.add("To do")
    t = manager.add("Will complete")
    manager.complete(t["id"])
    todos = manager.list_todos(show_done=True)
    assert len(todos) == 2


# --- Complete ---

def test_complete_marks_done(manager):
    t = manager.add("Finish report")
    result = manager.complete(t["id"])
    assert result["done"] is True

def test_complete_nonexistent_raises(manager):
    with pytest.raises(ValueError):
        manager.complete(9999)


# --- Delete ---

def test_delete_removes_todo(manager):
    t = manager.add("Temporary")
    manager.delete(t["id"])
    todos = manager.list_todos(show_done=True)
    assert all(todo["id"] != t["id"] for todo in todos)

def test_delete_returns_deleted(manager):
    t = manager.add("To remove")
    deleted = manager.delete(t["id"])
    assert deleted["title"] == "To remove"

def test_delete_nonexistent_raises(manager):
    with pytest.raises(ValueError):
        manager.delete(9999)


# --- Search ---

def test_search_finds_match(manager):
    manager.add("Buy groceries")
    manager.add("Buy new laptop")
    manager.add("Clean house")
    results = manager.search("buy")
    assert len(results) == 2

def test_search_case_insensitive(manager):
    manager.add("IMPORTANT Meeting")
    results = manager.search("important")
    assert len(results) == 1

def test_search_no_match(manager):
    manager.add("Something")
    results = manager.search("xyz")
    assert results == []


# --- Persistence ---

def test_persistence_across_instances(storage_path):
    TodoManager = load_solution()
    m1 = TodoManager(storage_path)
    m1.add("Persistent task")
    m2 = TodoManager(storage_path)
    todos = m2.list_todos()
    assert any(t["title"] == "Persistent task" for t in todos)

def test_persistence_preserves_done_state(storage_path):
    TodoManager = load_solution()
    m1 = TodoManager(storage_path)
    t = m1.add("Complete me")
    m1.complete(t["id"])
    m2 = TodoManager(storage_path)
    todos = m2.list_todos(show_done=True)
    matched = [todo for todo in todos if todo["id"] == t["id"]]
    assert len(matched) == 1
    assert matched[0]["done"] is True
