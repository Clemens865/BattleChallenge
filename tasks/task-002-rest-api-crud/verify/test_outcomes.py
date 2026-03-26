"""Outcome-based tests for REST API CRUD task."""
import subprocess
import time
import os
import signal
import pytest
import httpx

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="module", autouse=True)
def server():
    """Start the server before tests and stop it after."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    app_path = os.path.join(output_dir, "app.py")
    if not os.path.exists(app_path):
        pytest.skip(f"app.py not found in {output_dir}")

    proc = subprocess.Popen(
        ["python3", app_path],
        cwd=output_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )

    # Wait for server to start
    for _ in range(20):
        try:
            httpx.get(f"{BASE_URL}/todos", timeout=1.0)
            break
        except (httpx.ConnectError, httpx.ReadTimeout):
            time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail("Server did not start within 10 seconds")

    yield proc

    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait(timeout=5)


def test_list_todos_empty():
    """Initially, todo list should be empty."""
    r = httpx.get(f"{BASE_URL}/todos")
    assert r.status_code == 200
    assert r.json() == []


def test_create_todo():
    """POST /todos creates a new todo."""
    r = httpx.post(f"{BASE_URL}/todos", json={"title": "Buy milk"})
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert "id" in data


def test_get_todo():
    """GET /todos/:id returns the todo."""
    create = httpx.post(f"{BASE_URL}/todos", json={"title": "Test get"})
    todo_id = create.json()["id"]

    r = httpx.get(f"{BASE_URL}/todos/{todo_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Test get"


def test_update_todo():
    """PUT /todos/:id updates the todo."""
    create = httpx.post(f"{BASE_URL}/todos", json={"title": "Test update"})
    todo_id = create.json()["id"]

    r = httpx.put(f"{BASE_URL}/todos/{todo_id}", json={"title": "Updated", "completed": True})
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"
    assert r.json()["completed"] is True


def test_delete_todo():
    """DELETE /todos/:id removes the todo."""
    create = httpx.post(f"{BASE_URL}/todos", json={"title": "Test delete"})
    todo_id = create.json()["id"]

    r = httpx.delete(f"{BASE_URL}/todos/{todo_id}")
    assert r.status_code == 204

    r = httpx.get(f"{BASE_URL}/todos/{todo_id}")
    assert r.status_code == 404


def test_get_nonexistent():
    """GET /todos/999999 returns 404."""
    r = httpx.get(f"{BASE_URL}/todos/999999")
    assert r.status_code == 404


def test_delete_nonexistent():
    """DELETE /todos/999999 returns 404."""
    r = httpx.delete(f"{BASE_URL}/todos/999999")
    assert r.status_code == 404


def test_list_todos_after_creates():
    """GET /todos returns all created todos."""
    r = httpx.get(f"{BASE_URL}/todos")
    assert r.status_code == 200
    assert len(r.json()) >= 1
