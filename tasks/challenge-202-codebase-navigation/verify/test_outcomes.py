"""Outcome-based tests for challenge-202: Large codebase navigation."""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input", "project")


def _overlay_project():
    """Copy input project to temp dir, overlay OUTPUT_DIR files on top."""
    tmp = tempfile.mkdtemp(prefix="c202_")
    shutil.copytree(INPUT_DIR, os.path.join(tmp, "project"))
    # Walk OUTPUT_DIR and overlay any files preserving directory structure
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            if not f.endswith(".py"):
                continue
            src = os.path.join(root, f)
            rel = os.path.relpath(src, OUTPUT_DIR)
            dst = os.path.join(tmp, "project", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    return tmp


def _read_file(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


def _find_files(directory, pattern="*.py"):
    """Recursively find files matching pattern."""
    import fnmatch
    matches = []
    for root, dirs, files in os.walk(directory):
        for f in fnmatch.filter(files, pattern):
            matches.append(os.path.join(root, f))
    return matches


def _all_output_content():
    """Concatenate all .py files in OUTPUT_DIR."""
    content = ""
    for f in _find_files(OUTPUT_DIR):
        content += _read_file(f) or ""
    return content


@pytest.fixture(scope="module")
def overlay_dir():
    d = _overlay_project()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def all_content():
    return _all_output_content()


# ===========================================================================
# SECTION 1: Rate limit middleware exists (5 tests)
# ===========================================================================

def test_rate_limit_middleware_exists():
    """A rate limiting middleware file must exist in the output."""
    all_files = _find_files(OUTPUT_DIR)
    names = [os.path.basename(f) for f in all_files]
    content = _all_output_content().lower()
    has_rate_file = any("rate" in n.lower() for n in names)
    has_rate_class = "ratelimit" in content.replace("_", "").replace("-", "")
    assert has_rate_file or has_rate_class, (
        "No rate limiting middleware file or class found in output"
    )


def test_rate_limit_has_before_method(all_content):
    """Rate limit middleware must have a before() method (matching the pattern)."""
    assert "def before" in all_content, (
        "Rate limit middleware must implement before() method per middleware pattern"
    )


def test_rate_limit_has_after_method(all_content):
    """Rate limit middleware must have an after() method (matching the pattern)."""
    assert "def after" in all_content, (
        "Rate limit middleware must implement after() method per middleware pattern"
    )


def test_rate_limit_returns_429(all_content):
    """Rate limit must return 429 status when limit exceeded."""
    assert "429" in all_content, "Rate limit middleware must return HTTP 429"


def test_rate_limit_error_message(all_content):
    """Error response should mention rate limit."""
    lower = all_content.lower()
    assert "rate limit" in lower or "rate_limit" in lower or "too many" in lower, (
        "Rate limit error message should mention rate limiting"
    )


# ===========================================================================
# SECTION 2: Config system integration (4 tests)
# ===========================================================================

def test_uses_config_system(all_content):
    """The middleware must import from the core config system."""
    assert "get_config" in all_content, (
        "Rate limit middleware must use get_config from core config system"
    )


def test_config_key_defined(all_content):
    """RATE_LIMIT_REQUESTS_PER_MINUTE must appear in the output."""
    assert "RATE_LIMIT_REQUESTS_PER_MINUTE" in all_content, (
        "Config key RATE_LIMIT_REQUESTS_PER_MINUTE must be defined"
    )


def test_config_default_60(all_content):
    """Default rate limit should be 60."""
    # Look for 60 near the config key
    assert "60" in all_content, "Default rate limit of 60 must be specified"


def test_config_key_in_defaults_or_get_config(all_content):
    """The config key must be used with get_config or added to defaults."""
    has_get = "get_config" in all_content and "RATE_LIMIT" in all_content
    has_default = "RATE_LIMIT_REQUESTS_PER_MINUTE" in all_content
    assert has_get or has_default


# ===========================================================================
# SECTION 3: Applied to correct endpoint (5 tests)
# ===========================================================================

def test_applied_to_users_endpoint(all_content):
    """Rate limiting must be applied to the /api/users POST endpoint."""
    lower = all_content.lower()
    has_users = "/api/users" in all_content or "users" in lower
    has_post = "post" in lower
    assert has_users and has_post, (
        "Rate limiting must target POST /api/users"
    )


def test_retry_after_in_response(all_content):
    """429 response should include retry_after information."""
    assert "retry_after" in all_content or "retry-after" in all_content.lower(), (
        "Rate limit response should include retry_after"
    )


def test_tracks_client_ip(all_content):
    """Rate limiter should track requests per client IP."""
    lower = all_content.lower()
    assert "client_ip" in lower or "ip" in lower or "remote_addr" in lower or "addr" in lower, (
        "Rate limiter should track by client IP"
    )


def test_uses_time_window(all_content):
    """Rate limiter must use a time-based window."""
    assert "time" in all_content.lower(), "Rate limiter must use time-based tracking"


def test_no_test_files_modified():
    """Test files in the output should not exist or be identical to originals."""
    test_files = [
        "packages/api/tests/test_routes.py",
        "packages/worker/tests/test_worker.py",
    ]
    for tf in test_files:
        out_path = os.path.join(OUTPUT_DIR, tf)
        if os.path.exists(out_path):
            orig_path = os.path.join(INPUT_DIR, tf)
            assert _read_file(out_path) == _read_file(orig_path), (
                f"Test file {tf} was modified"
            )


# ===========================================================================
# SECTION 4: Follows existing middleware pattern (4 tests)
# ===========================================================================

def test_uses_existing_middleware_pattern(all_content):
    """Rate limit middleware should follow the class-based pattern with before/after."""
    # Look for class definition
    has_class = bool(re.search(r"class\s+\w*[Rr]ate\w*", all_content))
    has_before = "def before" in all_content
    has_after = "def after" in all_content
    assert has_class and has_before and has_after, (
        "Must follow class-based middleware pattern with before() and after() methods"
    )


def test_middleware_class_has_init(all_content):
    """Middleware class should have __init__ like the auth middleware."""
    assert "def __init__" in all_content


def test_imports_from_core(all_content):
    """Middleware should import from the core package."""
    assert "core" in all_content.lower(), (
        "Rate limit middleware should import from core package"
    )


def test_uses_logger(all_content):
    """Middleware should use the logging system."""
    has_logger = "get_logger" in all_content or "logger" in all_content.lower()
    assert has_logger, "Middleware should use the core logging system"


# ===========================================================================
# SECTION 5: Behavioral tests via overlaid project (7 tests)
# ===========================================================================

def _make_app(overlay_dir):
    """Create an Application instance from the overlaid project."""
    sys.path.insert(0, overlay_dir)
    # Clear any cached modules
    mods_to_remove = [k for k in sys.modules if k.startswith("packages")]
    for m in mods_to_remove:
        del sys.modules[m]
    from packages.core.src.config import set_config, reset_config
    from packages.core.src.database import db
    reset_config()
    set_config("AUTH_ENABLED", False)
    db.clear_table("users")
    db.clear_table("teams")
    from packages.api.src.app import Application
    return Application()


def test_health_still_works(overlay_dir):
    """GET /api/health should still work (no rate limiting)."""
    app = _make_app(overlay_dir)
    result = app.handle_request("GET", "/api/health")
    assert result["status"] == 200


def test_create_user_still_works(overlay_dir):
    """POST /api/users should work for a single request."""
    app = _make_app(overlay_dir)
    result = app.handle_request("POST", "/api/users", body={
        "name": "Test User", "email": "test@example.com",
    })
    assert result["status"] == 201


def test_create_team_still_works(overlay_dir):
    """POST /api/teams should work (no rate limiting on teams)."""
    app = _make_app(overlay_dir)
    result = app.handle_request("POST", "/api/teams", body={
        "name": "Test Team",
    })
    assert result["status"] == 201


def test_other_endpoints_unaffected(overlay_dir):
    """GET /api/health should not be rate-limited even with many requests."""
    app = _make_app(overlay_dir)
    for i in range(100):
        result = app.handle_request("GET", "/api/health")
        assert result["status"] == 200, f"Health check failed on request {i + 1}"


def test_rate_limit_works(overlay_dir):
    """Making many rapid POST /api/users requests should eventually return 429."""
    app = _make_app(overlay_dir)
    # Set a low rate limit for testing
    from packages.core.src.config import set_config
    set_config("RATE_LIMIT_REQUESTS_PER_MINUTE", 5)
    # Reimport to pick up the config change
    mods_to_remove = [k for k in sys.modules if k.startswith("packages.api")]
    for m in mods_to_remove:
        del sys.modules[m]
    from packages.api.src.app import Application
    app = Application()
    got_429 = False
    for i in range(20):
        result = app.handle_request(
            "POST", "/api/users",
            body={"name": f"User{i}", "email": f"u{i}@test.com"},
            client_ip="10.0.0.1",
        )
        if result.get("status") == 429:
            got_429 = True
            break
    assert got_429, "Rate limiting never triggered after 20 rapid requests with limit=5"


def test_rate_limit_per_ip(overlay_dir):
    """Different IPs should have independent rate limits."""
    app = _make_app(overlay_dir)
    from packages.core.src.config import set_config
    set_config("RATE_LIMIT_REQUESTS_PER_MINUTE", 3)
    mods_to_remove = [k for k in sys.modules if k.startswith("packages.api")]
    for m in mods_to_remove:
        del sys.modules[m]
    from packages.api.src.app import Application
    app = Application()
    # Exhaust limit for IP 1
    for i in range(10):
        app.handle_request(
            "POST", "/api/users",
            body={"name": f"A{i}", "email": f"a{i}@test.com"},
            client_ip="10.0.0.1",
        )
    # IP 2 should still work
    result = app.handle_request(
        "POST", "/api/users",
        body={"name": "B0", "email": "b0@test.com"},
        client_ip="10.0.0.2",
    )
    assert result["status"] in (201, 409), (
        f"Different IP should not be rate-limited, got {result['status']}"
    )


def test_no_unrelated_files_modified():
    """At most 5 files should be in the output."""
    all_files = _find_files(OUTPUT_DIR)
    assert len(all_files) <= 8, (
        f"Too many files modified ({len(all_files)}). "
        "Only rate limit middleware, config, routes, and app should change."
    )
