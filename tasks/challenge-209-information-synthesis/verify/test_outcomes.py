"""Outcome-based tests for challenge-209: Multi-Source Information Synthesis.

Verifies that the API client was correctly updated from v1 to v2 using
information from ALL 4 input sources: client code, changelog, API docs, slack thread.
"""
import ast
import importlib.util
import inspect
import os
import re
import sys
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _read_source():
    path = os.path.join(OUTPUT_DIR, "api_client.py")
    if not os.path.exists(path):
        pytest.skip(f"api_client.py not found in {OUTPUT_DIR}")
    with open(path, "r") as f:
        return f.read()


def _load_module():
    path = os.path.join(OUTPUT_DIR, "api_client.py")
    if not os.path.exists(path):
        pytest.skip(f"api_client.py not found in {OUTPUT_DIR}")
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec = importlib.util.spec_from_file_location("api_client", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def src():
    return _read_source()


@pytest.fixture(scope="module")
def mod():
    return _load_module()


# ===========================================================================
# SECTION 1: URL migration — v1 -> v2 (3 tests)
# Source: changelog + client code
# ===========================================================================

def test_uses_v2_base_url(src):
    """Base URL must use /v2/ not /v1/."""
    assert "/v2" in src, "Base URL must use /v2 prefix"


def test_no_v1_urls(src):
    """No remaining /v1/ references."""
    # Allow v1 in comments but not in string literals used as URLs
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert "/v1/" not in code_without_comments, \
        "All /v1/ URL references must be replaced with /v2/"


def test_base_url_correct(src):
    """Base URL should be the full v2 URL."""
    assert re.search(r'https://api\.datastore\.example\.com/v2', src), \
        "BASE_URL must point to the v2 API"


# ===========================================================================
# SECTION 2: Authentication — API key -> Bearer token (3 tests)
# Source: changelog
# ===========================================================================

def test_uses_bearer_auth(src):
    """Authorization header must use Bearer token."""
    assert re.search(r"(?i)bearer", src), \
        "Auth must use Bearer token (from changelog)"


def test_no_api_key_header(src):
    """X-API-Key header must be removed."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert "X-API-Key" not in code_without_comments, \
        "X-API-Key header must be removed (from changelog)"


def test_authorization_header(src):
    """Headers must include Authorization: Bearer <token>."""
    assert re.search(r'["\']Authorization["\']', src), \
        "Must set Authorization header for Bearer auth"


# ===========================================================================
# SECTION 3: Response format — XML -> JSON (3 tests)
# Source: changelog
# ===========================================================================

def test_parses_json_not_xml(src):
    """Response parsing must use json, not XML."""
    assert re.search(r"(?i)(json|\.json\(\))", src), \
        "Must parse JSON responses (from changelog)"


def test_no_xml_parsing(src):
    """No XML parsing code remaining."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert "xml.etree" not in code_without_comments and "ET.fromstring" not in code_without_comments, \
        "XML parsing must be removed"


def test_no_xml_imports(src):
    """No leftover XML imports."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert not re.search(r"^\s*import\s+xml", code_without_comments, re.MULTILINE), \
        "XML imports must be removed"


# ===========================================================================
# SECTION 4: Content type headers (2 tests)
# Source: changelog + API docs
# ===========================================================================

def test_accepts_json(src):
    """Accept header must request JSON."""
    assert re.search(r"(?i)application/json", src), \
        "Must set Accept/Content-Type to application/json"


def test_no_xml_content_type(src):
    """No remaining XML content type references."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert "application/xml" not in code_without_comments, \
        "Must not use application/xml content type"


# ===========================================================================
# SECTION 5: Cursor-based pagination (3 tests)
# Source: Slack thread (Sarah's message about pagination)
# ===========================================================================

def test_cursor_pagination(src):
    """Pagination must use cursor parameter, not offset."""
    assert re.search(r"(?i)cursor", src), \
        "Must use cursor-based pagination (from Slack thread)"


def test_no_offset_pagination(src):
    """Offset-based pagination must be removed."""
    # Check that offset isn't used as a pagination parameter
    # Allow "offset" in non-pagination contexts
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert not re.search(r"offset\s*=\s*\d+", code_without_comments), \
        "Offset-based pagination must be replaced with cursor-based"


def test_handles_next_cursor(src):
    """Must handle next_cursor from response for pagination."""
    assert re.search(r"(?i)(next_cursor|has_more)", src), \
        "Must handle next_cursor or has_more for pagination (from Slack thread + API docs)"


# ===========================================================================
# SECTION 6: Rate limit header (2 tests)
# Source: Slack thread (Mike and Sarah's exchange)
# ===========================================================================

def test_new_rate_limit_header(src):
    """Must read X-Rate-Limit-Remaining header."""
    assert re.search(r"X-Rate-Limit-Remaining", src), \
        "Must use X-Rate-Limit-Remaining header (from Slack thread)"


def test_no_old_rate_limit_header(src):
    """Old X-RateLimit header must be removed."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    # X-Rate-Limit-Remaining should be there, but not the old X-RateLimit (without dashes)
    # Remove the new header name first to check for old one
    cleaned = code_without_comments.replace("X-Rate-Limit-Remaining", "")
    assert "X-RateLimit" not in cleaned, \
        "Old X-RateLimit header must be replaced with X-Rate-Limit-Remaining"


# ===========================================================================
# SECTION 7: All 6 endpoints present (6 tests)
# Source: API docs v2
# ===========================================================================

def test_has_list_items_method(mod):
    """Client must have a method for listing items."""
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        # Try to find any class
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    assert client_class is not None, "Must define a client class"
    instance_methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(list.*item|get.*items)", m) for m in instance_methods), \
        "Must have list_items method"


def test_has_get_item_method(mod):
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(get_item\b|fetch_item|retrieve_item)", m) for m in methods), \
        "Must have get_item method"


def test_has_create_item_method(mod):
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(create_item|add_item|post_item)", m) for m in methods), \
        "Must have create_item method"


def test_has_update_item_method(mod):
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(update_item|edit_item|put_item)", m) for m in methods), \
        "Must have update_item method"


def test_has_delete_item_method(mod):
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(delete_item|remove_item)", m) for m in methods), \
        "Must have delete_item method"


def test_has_search_method(mod):
    """Client must have a search method (new in v2)."""
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    assert any(re.search(r"(?i)(search)", m) for m in methods), \
        "Must have search method (new endpoint from API docs)"


# ===========================================================================
# SECTION 8: Error handling (3 tests)
# Source: Slack thread (Sarah's comment about silent errors)
# ===========================================================================

def test_error_handling_exists(src):
    """Must raise exceptions for non-200 responses."""
    assert re.search(r"(?i)(raise|exception|error|HTTPError)", src), \
        "Must raise exceptions for error responses (from Slack thread)"


def test_checks_status_code(src):
    """Must check HTTP status code of responses."""
    assert re.search(r"(?i)(status_code|status|getcode|\.code|response\.ok)", src), \
        "Must check response status code"


def test_no_silent_failure(src):
    """Must not silently return None on error."""
    # Check the _make_request or equivalent doesn't just return None
    assert re.search(r"(?i)(raise|throw|exception)", src), \
        "Must not silently swallow errors — raise exceptions"


# ===========================================================================
# SECTION 9: JSON request body (2 tests)
# Source: changelog + API docs
# ===========================================================================

def test_sends_json_body(src):
    """Request bodies must be JSON, not XML."""
    assert re.search(r"(?i)(json\.dumps|json_data|data=.*json|json=)", src), \
        "Must send JSON request bodies"


def test_no_dict_to_xml(src):
    """dict_to_xml helper must be removed."""
    lines = [l for l in src.split("\n") if not l.strip().startswith("#")]
    code_without_comments = "\n".join(lines)
    assert "dict_to_xml" not in code_without_comments and "_to_xml" not in code_without_comments, \
        "XML conversion helpers must be removed"


# ===========================================================================
# SECTION 10: Information source coverage (3 tests)
# These specifically test that info from each source was used
# ===========================================================================

def test_changelog_info_used(src):
    """Bearer auth proves changelog was read."""
    assert re.search(r"(?i)bearer", src), \
        "Bearer auth (from changelog) must be implemented"


def test_docs_info_used(mod):
    """All 6 endpoints proves API docs were read."""
    client_class = getattr(mod, "DataStoreClient", None)
    if client_class is None:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            client_class = obj
            break
    methods = [m for m in dir(client_class) if not m.startswith("_")]
    method_str = " ".join(methods).lower()
    assert "search" in method_str, \
        "Search method (from API docs) must exist — proves docs were read"


def test_slack_info_used(src):
    """Cursor pagination + new rate limit header proves Slack thread was read."""
    has_cursor = re.search(r"(?i)cursor", src)
    has_rate_limit = re.search(r"X-Rate-Limit-Remaining", src)
    assert has_cursor and has_rate_limit, \
        "Cursor pagination and X-Rate-Limit-Remaining (from Slack thread) must be present"
