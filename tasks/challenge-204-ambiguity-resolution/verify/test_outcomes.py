"""Outcome-based tests for challenge-204: Specification Ambiguity Resolution."""

import ast
import importlib.util
import os
import re
import subprocess
import sys
import textwrap

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


def _find_python_files(subdir=""):
    """Return list of .py files in OUTPUT_DIR/subdir."""
    target = os.path.join(OUTPUT_DIR, subdir) if subdir else OUTPUT_DIR
    result = []
    if not os.path.isdir(target):
        return result
    for root, _dirs, files in os.walk(target):
        for fname in files:
            if fname.endswith(".py"):
                result.append(os.path.join(root, fname))
    return result


def _all_python_source():
    """Concatenate all .py file contents in OUTPUT_DIR."""
    parts = []
    for fpath in _find_python_files():
        with open(fpath, encoding="utf-8", errors="replace") as f:
            parts.append(f.read())
    return "\n".join(parts)


def _load_module(name, filename=None):
    """Dynamically load a module from OUTPUT_DIR."""
    filename = filename or f"{name}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found in {OUTPUT_DIR}")
    # Ensure OUTPUT_DIR is on sys.path so intra-project imports work
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# SECTION 1: DECISIONS.md — ambiguity documentation (7 tests)
# ===========================================================================

def test_decisions_file_exists():
    """DECISIONS.md must exist."""
    path = os.path.join(OUTPUT_DIR, "DECISIONS.md")
    assert os.path.isfile(path), "DECISIONS.md not found in output"


def test_decisions_has_substance():
    """DECISIONS.md must have meaningful content (>100 chars)."""
    content = _read_file("DECISIONS.md")
    assert content is not None
    assert len(content.strip()) > 100, (
        f"DECISIONS.md is too short ({len(content.strip())} chars)"
    )


def test_decisions_cover_events():
    """DECISIONS.md must discuss which events trigger notifications."""
    content = (_read_file("DECISIONS.md") or "").lower()
    event_keywords = ["event", "trigger", "action", "occur", "happen", "when"]
    assert any(kw in content for kw in event_keywords), (
        "DECISIONS.md does not discuss which events trigger notifications"
    )


def test_decisions_cover_channels():
    """DECISIONS.md must discuss delivery channel choices."""
    content = (_read_file("DECISIONS.md") or "").lower()
    channel_keywords = [
        "channel", "deliver", "email", "in-app", "push", "sms",
        "log", "store", "queue", "method", "medium",
    ]
    assert any(kw in content for kw in channel_keywords), (
        "DECISIONS.md does not discuss delivery channels"
    )


def test_decisions_cover_timing():
    """DECISIONS.md must discuss timing or SLA for notifications."""
    content = (_read_file("DECISIONS.md") or "").lower()
    timing_keywords = [
        "time", "timely", "immediate", "async", "synchron", "delay",
        "real-time", "realtime", "queue", "batch", "sla", "latency",
    ]
    assert any(kw in content for kw in timing_keywords), (
        "DECISIONS.md does not discuss timing expectations"
    )


def test_decisions_cover_extensibility():
    """DECISIONS.md must discuss extensibility approach."""
    content = (_read_file("DECISIONS.md") or "").lower()
    ext_keywords = [
        "extensib", "extend", "plugin", "registry", "pattern",
        "abstract", "interface", "base class", "protocol", "hook",
        "add new", "adding new", "scalab",
    ]
    assert any(kw in content for kw in ext_keywords), (
        "DECISIONS.md does not discuss extensibility"
    )


def test_decisions_multiple_sections():
    """DECISIONS.md should have multiple sections (headings or bullets)."""
    content = _read_file("DECISIONS.md") or ""
    headings = re.findall(r"^#{1,4}\s+.+", content, re.MULTILINE)
    bullets = re.findall(r"^[\-\*]\s+.+", content, re.MULTILINE)
    numbered = re.findall(r"^\d+[\.\)]\s+.+", content, re.MULTILINE)
    total_structure = len(headings) + len(bullets) + len(numbered)
    assert total_structure >= 4, (
        f"DECISIONS.md lacks structure (found {total_structure} headings/bullets, need >=4)"
    )


# ===========================================================================
# SECTION 2: Notification module existence & importability (5 tests)
# ===========================================================================

def test_notification_module_exists():
    """At least one new Python file related to notifications must exist."""
    all_py = _find_python_files()
    original_names = {
        "app.py", "models.py", "routes.py", "auth.py",
        "database.py", "utils.py", "config.py",
        "__init__.py", "test_routes.py",
    }
    new_files = [
        f for f in all_py
        if os.path.basename(f) not in original_names
    ]
    assert len(new_files) > 0, "No new Python files found for notification system"


def test_notification_is_importable():
    """A notification-related module must be importable."""
    all_py = _find_python_files()
    notification_files = [
        f for f in all_py
        if "notif" in os.path.basename(f).lower()
    ]
    if not notification_files:
        # Try loading any new file
        original_names = {
            "app.py", "models.py", "routes.py", "auth.py",
            "database.py", "utils.py", "config.py",
            "__init__.py", "test_routes.py",
        }
        notification_files = [
            f for f in all_py
            if os.path.basename(f) not in original_names
        ]
    assert len(notification_files) > 0, "No notification module found"
    # Try to import at least one
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    loaded = False
    for fpath in notification_files:
        name = os.path.splitext(os.path.basename(fpath))[0]
        try:
            spec = importlib.util.spec_from_file_location(name, fpath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            loaded = True
            break
        except Exception:
            continue
    assert loaded, "Could not import any notification module"


def test_has_send_or_notify_function():
    """Notification code must expose a send/notify callable."""
    all_source = _all_python_source()
    pattern = r"def\s+(send_notification|notify|dispatch|emit|create_notification|send|deliver)"
    matches = re.findall(pattern, all_source)
    assert len(matches) > 0, (
        "No send_notification / notify / dispatch / emit function found"
    )


def test_notification_has_recipient():
    """Notification functions must accept or reference a recipient/user."""
    all_source = _all_python_source()
    recipient_patterns = [
        r"recipient", r"user_id", r"user", r"to_user", r"target",
        r"addressee", r"receiver",
    ]
    found = any(re.search(p, all_source) for p in recipient_patterns)
    assert found, "Notification code does not reference a recipient"


def test_notification_has_content():
    """Notifications must have a message/body/content field."""
    all_source = _all_python_source()
    content_patterns = [
        r"message", r"content", r"body", r"text", r"payload",
        r"subject", r"title",
    ]
    found = any(re.search(p, all_source) for p in content_patterns)
    assert found, "Notification code does not reference message content"


# ===========================================================================
# SECTION 3: Integration with existing app (5 tests)
# ===========================================================================

def test_integrates_with_existing_models():
    """Notification code imports from existing app modules."""
    all_source = _all_python_source()
    # Check for imports of existing modules
    import_patterns = [
        r"from\s+models\s+import", r"import\s+models",
        r"from\s+database\s+import", r"import\s+database",
        r"from\s+auth\s+import", r"import\s+auth",
        r"from\s+app\s+import", r"import\s+app",
        r"from\s+utils\s+import", r"import\s+utils",
        r"from\s+routes\s+import", r"import\s+routes",
        r"User", r"Post",
    ]
    found = sum(1 for p in import_patterns if re.search(p, all_source))
    assert found >= 2, (
        "Notification code does not reference existing app modules"
    )


def test_handles_user_creation_event():
    """Code must handle a user-creation-related event."""
    all_source = _all_python_source().lower()
    patterns = [
        "user_created", "user_creation", "new_user", "user_registered",
        "registration", "signup", "sign_up", "create_user", "user_signup",
        "account_created",
    ]
    assert any(p in all_source for p in patterns), (
        "No user creation event handler found"
    )


def test_handles_post_creation_event():
    """Code must handle a post-creation-related event."""
    all_source = _all_python_source().lower()
    patterns = [
        "post_created", "post_creation", "new_post", "post_published",
        "article_created", "content_created", "create_post",
    ]
    assert any(p in all_source for p in patterns), (
        "No post creation event handler found"
    )


def test_original_app_files_present():
    """All 8 original project files must be present in output."""
    required = ["app.py", "models.py", "routes.py", "auth.py",
                 "database.py", "utils.py", "config.py"]
    for fname in required:
        path = os.path.join(OUTPUT_DIR, fname)
        assert os.path.isfile(path), f"Original file {fname} missing from output"


def test_existing_tests_still_pass():
    """The original test suite must still pass."""
    test_file = os.path.join(OUTPUT_DIR, "tests", "test_routes.py")
    if not os.path.isfile(test_file):
        # Try flat layout
        test_file = os.path.join(OUTPUT_DIR, "test_routes.py")
    if not os.path.isfile(test_file):
        pytest.skip("test_routes.py not found in output")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-x", "-q"],
        capture_output=True, text=True, cwd=OUTPUT_DIR, timeout=30,
    )
    assert result.returncode == 0, (
        f"Original tests failed:\n{result.stdout}\n{result.stderr}"
    )


# ===========================================================================
# SECTION 4: Extensibility architecture (5 tests)
# ===========================================================================

def test_extensible_event_types():
    """Event types should be extensible (registry, enum, dict, list, or subclass pattern)."""
    all_source = _all_python_source()
    extensibility_patterns = [
        r"class\s+\w*[Ee]vent\w*",            # Event base class
        r"[Ee]num",                             # Enum usage
        r"registry", r"_registry",              # Registry pattern
        r"register_event", r"register_handler", # Registration functions
        r"handlers\s*[=:]\s*\{",               # Handler dictionary
        r"handlers\s*[=:]\s*\[",               # Handler list
        r"subscribe", r"on_event",             # Observer pattern
        r"EventType", r"event_type",           # Event type references
        r"EVENT_TYPES",                         # Constants
        r"dispatch",                            # Dispatcher
        r"listener",                            # Listener pattern
    ]
    found = sum(1 for p in extensibility_patterns if re.search(p, all_source))
    assert found >= 2, (
        "Notification system does not use extensible patterns for event types"
    )


def test_extensible_channels():
    """Delivery channels should be extensible (not hardcoded to one method)."""
    all_source = _all_python_source()
    channel_patterns = [
        r"class\s+\w*[Cc]hannel\w*",           # Channel base class
        r"class\s+\w*[Dd]eliver\w*",           # Delivery base class
        r"class\s+\w*[Hh]andler\w*",           # Handler classes
        r"class\s+\w*[Nn]otifier\w*",          # Notifier classes
        r"class\s+\w*[Pp]rovider\w*",          # Provider classes
        r"channels\s*[=:]\s*[\{\[]",           # Channel collection
        r"register_channel",                    # Channel registration
        r"add_channel",                         # Channel addition
        r"@abc\.abstract",                      # Abstract methods
        r"ABC\)",                               # ABC subclass
        r"Protocol\)",                          # Protocol usage
        r"NotImplementedError",                 # Template pattern
    ]
    found = sum(1 for p in channel_patterns if re.search(p, all_source))
    assert found >= 1, (
        "Notification system does not use extensible patterns for channels"
    )


def test_no_hardcoded_events():
    """Event types should not be scattered hardcoded strings."""
    all_py = _find_python_files()
    original_names = {
        "app.py", "models.py", "routes.py", "auth.py",
        "database.py", "utils.py", "config.py",
        "__init__.py", "test_routes.py",
    }
    new_files = [
        f for f in all_py
        if os.path.basename(f) not in original_names
    ]
    if not new_files:
        pytest.skip("No new files found")

    # Look for centralized event definition (enum, constants, dict)
    all_new_source = ""
    for fpath in new_files:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            all_new_source += f.read() + "\n"

    centralized_patterns = [
        r"class\s+\w*[Ee]vent",
        r"[A-Z_]+_EVENT",
        r"EVENT_TYPES\s*=",
        r"events\s*=\s*\{",
        r"[Ee]num",
        r"EVENTS\s*=",
    ]
    found = any(re.search(p, all_new_source) for p in centralized_patterns)
    assert found, "Event types appear to be scattered strings rather than centralized"


def test_separation_of_concerns():
    """Notification logic should be separated from existing route handlers."""
    routes_content = _read_file("routes.py") or ""
    # The notification logic should NOT be dumped into routes.py
    notification_heavy_patterns = [
        r"class\s+\w*[Nn]otif",
        r"def\s+send_notification",
        r"def\s+dispatch",
        r"notification_channel",
    ]
    inline_count = sum(
        1 for p in notification_heavy_patterns
        if re.search(p, routes_content)
    )
    assert inline_count <= 1, (
        "Notification logic is inlined in routes.py instead of separated"
    )


def test_no_broken_imports():
    """All Python files should parse without syntax errors."""
    all_py = _find_python_files()
    for fpath in all_py:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            source = f.read()
        try:
            ast.parse(source, filename=fpath)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {os.path.basename(fpath)}: {e}")


# ===========================================================================
# SECTION 5: Code quality & robustness (6 tests)
# ===========================================================================

def test_error_handling_in_notifications():
    """Notification code should have try/except or error handling."""
    all_source = _all_python_source()
    error_patterns = [
        r"try\s*:", r"except\s+", r"raise\s+",
        r"logging\.", r"logger\.", r"log\.",
        r"Error\(", r"Exception\(",
    ]
    found = sum(1 for p in error_patterns if re.search(p, all_source))
    assert found >= 1, "Notification code has no error handling"


def test_notification_data_structure():
    """A Notification data structure (class/dataclass/dict factory) should exist."""
    all_source = _all_python_source()
    patterns = [
        r"class\s+Notification",
        r"@dataclass.*\nclass\s+\w*[Nn]otif",
        r"Notification\s*=\s*namedtuple",
        r"def\s+create_notification",
        r"TypedDict.*[Nn]otif",
        r"[Nn]otification.*=\s*\{",
    ]
    found = any(re.search(p, all_source, re.MULTILINE) for p in patterns)
    assert found, "No Notification data structure found"


def test_has_docstrings():
    """New notification code should include docstrings."""
    all_py = _find_python_files()
    original_names = {
        "app.py", "models.py", "routes.py", "auth.py",
        "database.py", "utils.py", "config.py",
        "__init__.py", "test_routes.py",
    }
    new_files = [
        f for f in all_py
        if os.path.basename(f) not in original_names
    ]
    if not new_files:
        pytest.skip("No new files found")

    has_docstring = False
    for fpath in new_files:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if '"""' in content or "'''" in content:
            has_docstring = True
            break
    assert has_docstring, "New notification files lack docstrings"


def test_minimum_code_size():
    """Notification implementation should be substantial (not a stub)."""
    all_py = _find_python_files()
    original_names = {
        "app.py", "models.py", "routes.py", "auth.py",
        "database.py", "utils.py", "config.py",
        "__init__.py", "test_routes.py",
    }
    new_files = [
        f for f in all_py
        if os.path.basename(f) not in original_names
    ]
    total_lines = 0
    for fpath in new_files:
        with open(fpath, encoding="utf-8", errors="replace") as f:
            total_lines += sum(1 for line in f if line.strip())
    assert total_lines >= 30, (
        f"Notification code is too small ({total_lines} non-empty lines, need >=30)"
    )


def test_timestamps_in_notifications():
    """Notifications should include timestamp information."""
    all_source = _all_python_source()
    timestamp_patterns = [
        r"timestamp", r"created_at", r"sent_at", r"datetime",
        r"time\.time", r"utcnow", r"isoformat",
    ]
    found = any(re.search(p, all_source) for p in timestamp_patterns)
    assert found, "Notification system does not track timestamps"


def test_read_status_or_acknowledgment():
    """Notifications should track read/sent status."""
    all_source = _all_python_source().lower()
    status_patterns = [
        "is_read", "read", "unread", "status", "sent",
        "delivered", "pending", "acknowledged", "seen",
    ]
    found = any(p in all_source for p in status_patterns)
    assert found, "Notification system does not track read/delivery status"
