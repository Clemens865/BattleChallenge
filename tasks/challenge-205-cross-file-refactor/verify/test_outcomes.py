"""Outcome-based tests for challenge-205: Cross-File Refactoring Consistency."""

import os
import re

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
TASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(TASK_DIR, "input", "project")


def _read_file(relative_path):
    """Read a file from OUTPUT_DIR, return contents or None."""
    path = os.path.join(OUTPUT_DIR, relative_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _find_all_ts_files():
    """Return list of all .ts files in OUTPUT_DIR (relative paths)."""
    result = []
    for root, _dirs, files in os.walk(OUTPUT_DIR):
        for fname in files:
            if fname.endswith(".ts"):
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, OUTPUT_DIR)
                result.append(rel)
    return sorted(result)


def _read_all_ts_content():
    """Read and concatenate all .ts file contents."""
    parts = []
    for rel in _find_all_ts_files():
        content = _read_file(rel)
        if content:
            parts.append(content)
    return "\n".join(parts)


def _count_occurrences(text, pattern):
    """Count regex occurrences in text."""
    return len(re.findall(pattern, text))


# ===========================================================================
# SECTION 1: No old references remain (6 tests)
# ===========================================================================

def test_no_user_service_class_references():
    """The string 'UserService' must not appear anywhere in the output."""
    all_content = _read_all_ts_content()
    # Allow it inside comments that explain the rename, but not in code
    # Strip comments for a more accurate check
    code_only = re.sub(r"//.*$", "", all_content, flags=re.MULTILINE)
    code_only = re.sub(r"/\*.*?\*/", "", code_only, flags=re.DOTALL)
    count = _count_occurrences(code_only, r"\bUserService\b")
    assert count == 0, (
        f"Found {count} remaining 'UserService' references in code"
    )


def test_no_get_user_method_references():
    """The method name 'getUser' must not appear anywhere in the output code."""
    all_content = _read_all_ts_content()
    code_only = re.sub(r"//.*$", "", all_content, flags=re.MULTILINE)
    code_only = re.sub(r"/\*.*?\*/", "", code_only, flags=re.DOTALL)
    # getUser should be gone but getUserByEmail can stay
    # We need to match getUser that is NOT followed by By
    count = _count_occurrences(code_only, r"\bgetUser\b(?!By)")
    assert count == 0, (
        f"Found {count} remaining 'getUser' references in code"
    )


def test_no_user_service_in_imports():
    """No import statement should reference 'UserService'."""
    all_content = _read_all_ts_content()
    import_lines = re.findall(r"^.*import.*UserService.*$", all_content, re.MULTILINE)
    assert len(import_lines) == 0, (
        f"Found {len(import_lines)} import(s) still referencing UserService"
    )


def test_no_user_service_filename():
    """No file should be named UserService.ts."""
    all_files = _find_all_ts_files()
    user_service_files = [f for f in all_files if "UserService" in f]
    assert len(user_service_files) == 0, (
        f"Found UserService filename(s): {user_service_files}"
    )


def test_no_user_service_variable_names():
    """Variable names 'userService' should be renamed to 'accountService'."""
    all_content = _read_all_ts_content()
    code_only = re.sub(r"//.*$", "", all_content, flags=re.MULTILINE)
    code_only = re.sub(r"/\*.*?\*/", "", code_only, flags=re.DOTALL)
    # Match userService as a variable (not part of a larger word)
    count = _count_occurrences(code_only, r"\buserService\b")
    assert count == 0, (
        f"Found {count} remaining 'userService' variable references"
    )


def test_no_user_service_in_test_mocks():
    """Test files should not mock or reference 'UserService'."""
    test_files = [f for f in _find_all_ts_files() if "test" in f.lower()]
    for tf in test_files:
        content = _read_file(tf) or ""
        code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
        count = _count_occurrences(code_only, r"\bUserService\b")
        assert count == 0, (
            f"Test file {tf} still references UserService ({count} times)"
        )


# ===========================================================================
# SECTION 2: New references exist (8 tests)
# ===========================================================================

def test_account_service_file_exists():
    """AccountService.ts must exist somewhere in the output."""
    all_files = _find_all_ts_files()
    account_files = [f for f in all_files if "AccountService" in f]
    assert len(account_files) > 0, "AccountService.ts not found"


def test_account_service_class_defined():
    """The AccountService class must be defined."""
    all_content = _read_all_ts_content()
    assert re.search(r"class\s+AccountService", all_content), (
        "AccountService class definition not found"
    )


def test_get_account_method_exists():
    """The getAccount method must exist in AccountService."""
    all_content = _read_all_ts_content()
    assert re.search(r"(?:async\s+)?getAccount\s*\(", all_content), (
        "getAccount method not found"
    )


def test_account_service_has_create_method():
    """AccountService should have createAccount (or createUser renamed)."""
    all_content = _read_all_ts_content()
    # createUser might stay as createUser since requirement only says rename getUser
    # But let's check for at least one of these methods
    has_create = re.search(r"(?:async\s+)?create(?:Account|User)\s*\(", all_content)
    assert has_create, "No create method found in AccountService"


def test_account_service_has_delete_method():
    """AccountService should have deleteAccount (or deleteUser renamed)."""
    all_content = _read_all_ts_content()
    has_delete = re.search(r"(?:async\s+)?delete(?:Account|User)\s*\(", all_content)
    assert has_delete, "No delete method found in AccountService"


def test_routes_import_account_service():
    """User routes should import AccountService."""
    content = _read_file(os.path.join("src", "routes", "users.ts"))
    if content is None:
        pytest.skip("src/routes/users.ts not found")
    assert "AccountService" in content, (
        "users.ts does not import AccountService"
    )


def test_tasks_route_uses_get_account():
    """tasks.ts should call getAccount instead of getUser."""
    content = _read_file(os.path.join("src", "routes", "tasks.ts"))
    if content is None:
        pytest.skip("src/routes/tasks.ts not found")
    assert "getAccount" in content, "tasks.ts does not use getAccount"


def test_auth_middleware_uses_get_account():
    """auth.ts middleware should use getAccount."""
    content = _read_file(os.path.join("src", "middleware", "auth.ts"))
    if content is None:
        pytest.skip("src/middleware/auth.ts not found")
    assert "getAccount" in content, "auth.ts does not use getAccount"


# ===========================================================================
# SECTION 3: All files present (5 tests)
# ===========================================================================

# The 28 original files (relative paths)
EXPECTED_FILES = [
    os.path.join("src", "index.ts"),
    os.path.join("src", "models", "User.ts"),
    os.path.join("src", "models", "Task.ts"),
    os.path.join("src", "models", "index.ts"),
    os.path.join("src", "services", "TaskService.ts"),
    os.path.join("src", "services", "NotificationService.ts"),
    os.path.join("src", "services", "index.ts"),
    os.path.join("src", "routes", "users.ts"),
    os.path.join("src", "routes", "tasks.ts"),
    os.path.join("src", "routes", "notifications.ts"),
    os.path.join("src", "routes", "health.ts"),
    os.path.join("src", "routes", "index.ts"),
    os.path.join("src", "middleware", "auth.ts"),
    os.path.join("src", "middleware", "validation.ts"),
    os.path.join("src", "middleware", "errorHandler.ts"),
    os.path.join("src", "middleware", "index.ts"),
    os.path.join("src", "utils", "crypto.ts"),
    os.path.join("src", "utils", "logger.ts"),
    os.path.join("src", "utils", "index.ts"),
    os.path.join("src", "config", "database.ts"),
    os.path.join("src", "config", "app.ts"),
    os.path.join("src", "config", "index.ts"),
    os.path.join("src", "types", "ServiceContainer.ts"),
    os.path.join("tests", "services"),  # directory check (file renamed)
    os.path.join("tests", "routes", "users.test.ts"),
    os.path.join("tests", "integration", "user-flow.test.ts"),
    os.path.join("tests", "middleware", "auth.test.ts"),
]

# Files that must exist as files (not the renamed one)
MUST_EXIST_FILES = [
    os.path.join("src", "index.ts"),
    os.path.join("src", "models", "User.ts"),
    os.path.join("src", "models", "Task.ts"),
    os.path.join("src", "services", "TaskService.ts"),
    os.path.join("src", "services", "NotificationService.ts"),
    os.path.join("src", "routes", "users.ts"),
    os.path.join("src", "routes", "tasks.ts"),
    os.path.join("src", "middleware", "auth.ts"),
    os.path.join("src", "middleware", "validation.ts"),
    os.path.join("src", "utils", "crypto.ts"),
    os.path.join("src", "utils", "logger.ts"),
    os.path.join("src", "config", "database.ts"),
    os.path.join("src", "config", "app.ts"),
    os.path.join("src", "types", "ServiceContainer.ts"),
]


@pytest.mark.parametrize("rel_path", MUST_EXIST_FILES)
def test_file_exists(rel_path):
    path = os.path.join(OUTPUT_DIR, rel_path)
    assert os.path.isfile(path), f"{rel_path} not found in output"


def test_minimum_file_count():
    """Output should have at least 25 .ts files."""
    all_files = _find_all_ts_files()
    assert len(all_files) >= 25, (
        f"Only {len(all_files)} .ts files found, expected >= 25"
    )


def test_user_model_unchanged():
    """The User model interface should NOT be renamed."""
    content = _read_file(os.path.join("src", "models", "User.ts"))
    if content is None:
        pytest.skip("User.ts not found")
    assert "interface User" in content, (
        "User interface was incorrectly renamed"
    )
    assert "UserRole" in content, "UserRole enum was incorrectly renamed"


def test_task_model_unchanged():
    """The Task model should be completely unchanged."""
    content = _read_file(os.path.join("src", "models", "Task.ts"))
    if content is None:
        pytest.skip("Task.ts not found")
    assert "interface Task" in content, "Task interface missing"


def test_no_unexpected_extra_files():
    """No completely unexpected files should appear (e.g., UserService.ts still existing alongside AccountService.ts)."""
    all_files = _find_all_ts_files()
    # UserService.ts should NOT coexist with AccountService.ts
    has_old = any("UserService.ts" in f for f in all_files)
    has_new = any("AccountService.ts" in f for f in all_files)
    if has_new:
        assert not has_old, (
            "Both UserService.ts and AccountService.ts exist — old file should be removed"
        )


# ===========================================================================
# SECTION 4: Consistency across specific files (8 tests)
# ===========================================================================

def test_service_container_uses_account_service():
    """ServiceContainer.ts should reference AccountService."""
    content = _read_file(os.path.join("src", "types", "ServiceContainer.ts"))
    if content is None:
        pytest.skip("ServiceContainer.ts not found")
    assert "AccountService" in content, "ServiceContainer still uses old name"
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "UserService" not in code_only, (
        "ServiceContainer still references UserService in code"
    )


def test_service_container_variable_renamed():
    """ServiceContainer should use accountService variable name."""
    content = _read_file(os.path.join("src", "types", "ServiceContainer.ts"))
    if content is None:
        pytest.skip("ServiceContainer.ts not found")
    assert "accountService" in content, (
        "ServiceContainer does not use accountService variable name"
    )


def test_notification_service_updated():
    """NotificationService should import and use AccountService."""
    content = _read_file(os.path.join("src", "services", "NotificationService.ts"))
    if content is None:
        pytest.skip("NotificationService.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "NotificationService still references UserService"
    )


def test_notification_service_uses_get_account():
    """NotificationService should call getAccount."""
    content = _read_file(os.path.join("src", "services", "NotificationService.ts"))
    if content is None:
        pytest.skip("NotificationService.ts not found")
    assert "getAccount" in content, (
        "NotificationService still calls getUser instead of getAccount"
    )


def test_task_service_uses_account_service():
    """TaskService should import AccountService."""
    content = _read_file(os.path.join("src", "services", "TaskService.ts"))
    if content is None:
        pytest.skip("TaskService.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "TaskService still references UserService"
    )


def test_task_service_calls_get_account():
    """TaskService should call getAccount."""
    content = _read_file(os.path.join("src", "services", "TaskService.ts"))
    if content is None:
        pytest.skip("TaskService.ts not found")
    assert "getAccount" in content, (
        "TaskService still calls getUser"
    )


def test_services_index_exports_account_service():
    """services/index.ts should export AccountService."""
    content = _read_file(os.path.join("src", "services", "index.ts"))
    if content is None:
        pytest.skip("services/index.ts not found")
    assert "AccountService" in content, (
        "services/index.ts does not export AccountService"
    )
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "UserService" not in code_only, (
        "services/index.ts still exports UserService"
    )


def test_main_index_uses_account_service():
    """src/index.ts should use AccountService naming."""
    content = _read_file(os.path.join("src", "index.ts"))
    if content is None:
        pytest.skip("src/index.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only or "accountService" in code_only, (
        "src/index.ts does not reference AccountService"
    )


# ===========================================================================
# SECTION 5: Test files updated (5 tests)
# ===========================================================================

def test_user_service_test_file_renamed_or_updated():
    """The UserService test file should reference AccountService."""
    # Check both possible locations
    possible = [
        os.path.join("tests", "services", "AccountService.test.ts"),
        os.path.join("tests", "services", "UserService.test.ts"),
    ]
    content = None
    for p in possible:
        content = _read_file(p)
        if content:
            break
    if content is None:
        pytest.skip("No service test file found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "Service test file does not reference AccountService"
    )


def test_user_routes_test_updated():
    """routes/users.test.ts should reference AccountService."""
    content = _read_file(os.path.join("tests", "routes", "users.test.ts"))
    if content is None:
        pytest.skip("users.test.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "users.test.ts still references UserService"
    )


def test_integration_test_updated():
    """user-flow.test.ts should reference AccountService."""
    content = _read_file(os.path.join("tests", "integration", "user-flow.test.ts"))
    if content is None:
        pytest.skip("user-flow.test.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "user-flow.test.ts still references UserService"
    )


def test_auth_test_updated():
    """auth.test.ts should reference AccountService."""
    content = _read_file(os.path.join("tests", "middleware", "auth.test.ts"))
    if content is None:
        pytest.skip("auth.test.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "auth.test.ts still references UserService"
    )


def test_test_mocks_use_get_account():
    """Test mocks should spy on getAccount not getUser."""
    test_files = [f for f in _find_all_ts_files() if "test" in f.lower()]
    all_test_content = ""
    for tf in test_files:
        content = _read_file(tf) or ""
        all_test_content += content + "\n"
    code_only = re.sub(r"//.*$", "", all_test_content, flags=re.MULTILINE)
    # Should have getAccount references, not getUser
    if "spyOn" in code_only or "mock" in code_only.lower():
        get_user_in_mocks = re.findall(r"""['""]getUser['""]""", code_only)
        assert len(get_user_in_mocks) == 0, (
            f"Found {len(get_user_in_mocks)} mock(s) still using 'getUser'"
        )


# ===========================================================================
# SECTION 6: Import path consistency (4 tests)
# ===========================================================================

def test_import_paths_reference_account_service():
    """All imports that referenced ./UserService should now reference ./AccountService."""
    all_content = _read_all_ts_content()
    old_imports = re.findall(
        r"""from\s+['""].*UserService['""]""", all_content
    )
    assert len(old_imports) == 0, (
        f"Found {len(old_imports)} import path(s) still referencing UserService"
    )


def test_new_import_paths_exist():
    """At least some files should import from AccountService path."""
    all_content = _read_all_ts_content()
    new_imports = re.findall(
        r"""from\s+['""].*AccountService['""]""", all_content
    )
    assert len(new_imports) >= 3, (
        f"Only {len(new_imports)} import(s) reference AccountService path, expected >= 3"
    )


def test_notification_route_updated():
    """notifications.ts route should reference AccountService."""
    content = _read_file(os.path.join("src", "routes", "notifications.ts"))
    if content is None:
        pytest.skip("notifications.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "AccountService" in code_only, (
        "notifications.ts still references UserService"
    )
    assert "getAccount" in code_only, (
        "notifications.ts still uses getUser"
    )


def test_middleware_auth_variable_renamed():
    """auth.ts middleware variable should be accountService not userService."""
    content = _read_file(os.path.join("src", "middleware", "auth.ts"))
    if content is None:
        pytest.skip("auth.ts not found")
    code_only = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    assert "accountService" in code_only, (
        "auth.ts still uses userService variable name"
    )
