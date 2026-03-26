"""Outcome-based tests for challenge-207: Long-Running Workflow Resilience.

Verifies that the generated REST API conforms to the OpenAPI spec and PRD.
Tests check file structure, response shapes, auth, pagination, validation,
search, and cross-file consistency.
"""
import importlib.util
import json
import os
import re
import sys
import sqlite3
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _file_exists(name):
    return os.path.exists(os.path.join(OUTPUT_DIR, name))


def _read_file(name):
    path = os.path.join(OUTPUT_DIR, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} not found in {OUTPUT_DIR}")
    with open(path, "r") as f:
        return f.read()


def _load_module(name):
    """Load a Python module from OUTPUT_DIR by name (without .py)."""
    path = os.path.join(OUTPUT_DIR, f"{name}.py")
    if not os.path.exists(path):
        pytest.skip(f"{name}.py not found in {OUTPUT_DIR}")
    # Add OUTPUT_DIR to sys.path so intra-project imports work
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# SECTION 1: Required files exist (8 tests)
# ===========================================================================

def test_models_file_exists():
    assert _file_exists("models.py"), "models.py is required"


def test_routes_file_exists():
    assert _file_exists("routes.py"), "routes.py is required"


def test_auth_file_exists():
    assert _file_exists("auth.py"), "auth.py is required"


def test_database_file_exists():
    assert _file_exists("database.py"), "database.py is required"


def test_migrations_file_exists():
    assert _file_exists("migrations.py"), "migrations.py is required"


def test_seed_file_exists():
    assert _file_exists("seed.py"), "seed.py is required"


def test_validators_file_exists():
    assert _file_exists("validators.py"), "validators.py is required"


def test_app_file_exists():
    assert _file_exists("app.py"), "app.py is required"


# ===========================================================================
# SECTION 2: Models define required tables/classes (4 tests)
# ===========================================================================

def test_models_has_item():
    src = _read_file("models.py")
    assert re.search(r"(?i)(class\s+Item|items?\s*=|CREATE\s+TABLE.*items)", src), \
        "models.py must define an Item model or items table"


def test_models_has_category():
    src = _read_file("models.py")
    assert re.search(r"(?i)(class\s+Categor|categor|CREATE\s+TABLE.*categor)", src), \
        "models.py must define a Category model"


def test_models_has_user():
    src = _read_file("models.py")
    assert re.search(r"(?i)(class\s+User|users?\s*=|CREATE\s+TABLE.*users)", src), \
        "models.py must define a User model"


def test_item_has_timestamps():
    src = _read_file("models.py")
    assert "created_at" in src and "updated_at" in src, \
        "Item model must have created_at and updated_at fields"


# ===========================================================================
# SECTION 3: Auth module (4 tests)
# ===========================================================================

def test_auth_has_jwt():
    src = _read_file("auth.py")
    assert re.search(r"(?i)(jwt|json.?web.?token|pyjwt|jose)", src), \
        "auth.py must use JWT tokens"


def test_auth_has_bearer():
    src = _read_file("auth.py")
    assert re.search(r"(?i)bearer", src), \
        "auth.py must handle Bearer token authentication"


def test_auth_has_secret_key():
    src = _read_file("auth.py")
    assert re.search(r"(?i)(secret|key|SECRET_KEY|JWT_SECRET)", src), \
        "auth.py must reference a secret key for JWT signing"


def test_auth_has_verify_or_decode():
    src = _read_file("auth.py")
    assert re.search(r"(?i)(verify|decode|validate)", src), \
        "auth.py must have token verification logic"


# ===========================================================================
# SECTION 4: Routes define all 6 endpoints (7 tests)
# ===========================================================================

def test_routes_has_list_items():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(get.*items|list.*items|/items)", src), \
        "routes.py must define GET /items endpoint"


def test_routes_has_create_item():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(post.*items?|create.*item)", src), \
        "routes.py must define POST /items endpoint"


def test_routes_has_get_item():
    src = _read_file("routes.py")
    # Look for route with item ID parameter
    assert re.search(r"(?i)(items?[/\[<{].*id|get_item|item_detail)", src), \
        "routes.py must define GET /items/:id endpoint"


def test_routes_has_update_item():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(put.*items?|update.*item|patch.*item)", src), \
        "routes.py must define PUT /items/:id endpoint"


def test_routes_has_delete_item():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(delete.*items?|remove.*item)", src), \
        "routes.py must define DELETE /items/:id endpoint"


def test_routes_has_categories():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(categor)", src), \
        "routes.py must define GET /categories endpoint"


def test_routes_has_search():
    src = _read_file("routes.py")
    assert re.search(r"(?i)(search|/search)", src), \
        "routes.py must define POST /search endpoint"


# ===========================================================================
# SECTION 5: Database setup (3 tests)
# ===========================================================================

def test_database_uses_sqlite():
    src = _read_file("database.py")
    assert re.search(r"(?i)(sqlite|sqlite3)", src), \
        "database.py must use SQLite"


def test_database_has_connection():
    src = _read_file("database.py")
    assert re.search(r"(?i)(connect|engine|session|get_db)", src), \
        "database.py must have connection logic"


def test_migrations_create_tables():
    src = _read_file("migrations.py")
    assert re.search(r"(?i)(create.*table|migrate|schema|init)", src), \
        "migrations.py must create database tables"


# ===========================================================================
# SECTION 6: Seed data (3 tests)
# ===========================================================================

def test_seed_has_categories():
    src = _read_file("seed.py")
    assert re.search(r"(?i)electronics", src) and re.search(r"(?i)books", src), \
        "seed.py must include Electronics and Books categories"


def test_seed_has_users():
    src = _read_file("seed.py")
    assert re.search(r"(?i)admin", src), \
        "seed.py must include admin user"


def test_seed_has_items():
    src = _read_file("seed.py")
    assert re.search(r"(?i)(wireless mouse|usb|keyboard|cotton|python handbook)", src), \
        "seed.py must include seed items from PRD"


# ===========================================================================
# SECTION 7: Validation (3 tests)
# ===========================================================================

def test_validators_check_name():
    src = _read_file("validators.py")
    assert re.search(r"(?i)(name|required)", src), \
        "validators.py must validate item name"


def test_validators_check_price():
    src = _read_file("validators.py")
    assert re.search(r"(?i)(price)", src), \
        "validators.py must validate item price"


def test_validators_return_errors():
    src = _read_file("validators.py")
    assert re.search(r"(?i)(error|detail|message|invalid|fail)", src), \
        "validators.py must return error messages"


# ===========================================================================
# SECTION 8: OpenAPI conformance — response shapes (8 tests)
# ===========================================================================

def test_list_response_has_pagination_fields():
    """GET /items response must have items, total, page, limit, pages."""
    src = _read_file("routes.py")
    for field in ["items", "total", "page", "limit", "pages"]:
        assert field in src, \
            f"List items response must include '{field}' field per OpenAPI spec"


def test_create_response_returns_item():
    """POST /items response must return the created item with id."""
    src = _read_file("routes.py")
    # The route should return the item with an id
    assert re.search(r"(?i)(id|created|201)", src), \
        "Create item route must return item with id and 201 status"


def test_delete_response_shape():
    """DELETE /items/:id response must have message and id fields."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(message.*delet|delet.*message|Item deleted)", src), \
        "Delete response must include 'message' field"


def test_error_format_consistent():
    """All error responses must use {"error": "...", "status": <code>} format."""
    src = _read_file("routes.py")
    # Check for consistent error format usage
    error_pattern = re.findall(r'["\']error["\']', src)
    assert len(error_pattern) >= 2, \
        "Routes must use consistent error format with 'error' field"


def test_categories_response_shape():
    """GET /categories must return {"categories": [...]}."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(categories)", src), \
        "Categories endpoint must return 'categories' array"


def test_search_response_shape():
    """POST /search must return {"results": [...], "count": N}."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(results|count)", src), \
        "Search endpoint must return 'results' and 'count'"


def test_item_not_found_returns_404():
    """Missing item returns {"error": "Item not found", "status": 404}."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(not.?found|404)", src), \
        "Routes must handle item not found with 404"


def test_validation_error_returns_422():
    """Invalid input returns 422 with error details."""
    src = _read_file("routes.py") + _read_file("validators.py")
    assert re.search(r"(?i)(422|validation|unprocessable)", src), \
        "Validation errors must return 422 status"


# ===========================================================================
# SECTION 9: Pagination logic (2 tests)
# ===========================================================================

def test_pagination_uses_page_and_limit():
    """Pagination must use page and limit parameters."""
    src = _read_file("routes.py")
    assert "page" in src and "limit" in src, \
        "List endpoint must accept page and limit parameters"


def test_pagination_calculates_pages():
    """Response must include total page count."""
    src = _read_file("routes.py")
    # Check for pages calculation (total / limit or ceil)
    assert re.search(r"(?i)(pages|ceil|math|//|\bdiv\b)", src), \
        "Pagination must calculate total pages"


# ===========================================================================
# SECTION 10: Search functionality (2 tests)
# ===========================================================================

def test_search_supports_name_filter():
    """Search must support filtering by name."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(name.*filter|filter.*name|LIKE|ilike|lower.*name)", src), \
        "Search must support name filtering (case-insensitive partial match)"


def test_search_supports_price_range():
    """Search must support min_price and max_price filters."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(min_price|max_price|price.*range)", src), \
        "Search must support price range filtering"


# ===========================================================================
# SECTION 11: Cross-file consistency (4 tests)
# ===========================================================================

def test_app_imports_routes():
    """app.py must import or reference routes."""
    src = _read_file("app.py")
    assert re.search(r"(?i)(import.*route|from.*route|routes)", src), \
        "app.py must import routes"


def test_app_imports_database():
    """app.py must import or reference database."""
    src = _read_file("app.py")
    assert re.search(r"(?i)(import.*database|from.*database|database|db)", src), \
        "app.py must import database module"


def test_routes_use_auth():
    """Routes must reference auth/authentication."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(auth|token|jwt|bearer|login_required|require_auth)", src), \
        "Routes must use authentication"


def test_routes_use_validators():
    """Routes must reference validation."""
    src = _read_file("routes.py")
    assert re.search(r"(?i)(valid|validator)", src), \
        "Routes must use input validation"


# ===========================================================================
# SECTION 12: Auth endpoints (2 tests)
# ===========================================================================

def test_auth_endpoint_exists():
    """Login endpoint must exist."""
    all_src = ""
    for f in ["routes.py", "auth.py", "app.py"]:
        if _file_exists(f):
            all_src += _read_file(f)
    assert re.search(r"(?i)(login|/auth|authenticate)", all_src), \
        "Login/auth endpoint must exist"


def test_unauthorized_returns_401():
    """Missing/invalid token must return 401."""
    src = _read_file("routes.py") + _read_file("auth.py")
    assert re.search(r"(?i)(401|unauthorized|Unauthorized)", src), \
        "Auth must return 401 for unauthorized requests"
