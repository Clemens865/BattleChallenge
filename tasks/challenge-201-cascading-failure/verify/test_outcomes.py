"""Outcome-based tests for challenge-201: Recovery from cascading failure."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input", "project")


def _overlay_project():
    """Copy input project to a temp dir, then overlay OUTPUT_DIR files on top."""
    tmp = tempfile.mkdtemp(prefix="c201_")
    shutil.copytree(INPUT_DIR, os.path.join(tmp, "project"))
    # Overlay fixed files from OUTPUT_DIR
    for name in os.listdir(OUTPUT_DIR):
        if name.endswith(".py") and not name.startswith("test_"):
            src = os.path.join(OUTPUT_DIR, name)
            dst = os.path.join(tmp, "project", name)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
    return tmp


def _read_file(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return f.read()


@pytest.fixture(scope="module")
def overlay_dir():
    d = _overlay_project()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def fixed_serializers(overlay_dir):
    path = os.path.join(overlay_dir, "project", "serializers.py")
    spec = importlib.util.spec_from_file_location("serializers", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def output_files():
    """List of .py files present in OUTPUT_DIR."""
    if not os.path.isdir(OUTPUT_DIR):
        return []
    return [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".py")]


# ===========================================================================
# SECTION 1: Root cause identification (4 tests)
# ===========================================================================

def test_root_cause_found(output_files):
    """The fix must be in serializers.py (the actual root cause), not api_handlers.py."""
    assert "serializers.py" in output_files, (
        "serializers.py must be in the output — that is where the root cause lives"
    )


def test_api_handlers_not_modified(output_files):
    """api_handlers.py should NOT be modified — the bug is not there."""
    if "api_handlers.py" in output_files:
        original = _read_file(os.path.join(INPUT_DIR, "api_handlers.py"))
        fixed = _read_file(os.path.join(OUTPUT_DIR, "api_handlers.py"))
        assert original == fixed, (
            "api_handlers.py was modified, but the bug is in serializers.py"
        )


def test_no_test_modifications(output_files):
    """Test files must not be modified."""
    assert "test_api.py" not in output_files, "test_api.py must not be modified"
    assert "test_models.py" not in output_files, "test_models.py must not be modified"


def test_minimal_changes(output_files):
    """At most 2 non-test files should be modified."""
    modified = [f for f in output_files if not f.startswith("test_")]
    assert len(modified) <= 2, f"Too many files modified: {modified}"


# ===========================================================================
# SECTION 2: Serializer correctness (6 tests)
# ===========================================================================

def test_serializer_handles_date(fixed_serializers):
    """_format_date must work with datetime.date objects."""
    from datetime import date
    result = fixed_serializers._format_date(date(2023, 6, 15))
    assert result == "2023-06-15"


def test_serializer_handles_datetime(fixed_serializers):
    """_format_date must work with datetime.datetime objects."""
    import datetime
    result = fixed_serializers._format_date(datetime.datetime(2023, 6, 15, 10, 30))
    assert result == "2023-06-15"


def test_serializer_handles_string_date(fixed_serializers):
    """_format_date should handle string dates gracefully."""
    # It should either return the string as-is or convert properly
    try:
        result = fixed_serializers._format_date("2023-06-15")
        assert "2023-06-15" in result
    except AttributeError:
        pytest.fail("_format_date still crashes on string input")


def test_serialize_book_with_date(fixed_serializers):
    """Full serialize_book works with a Book that has a date field."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(INPUT_DIR)))
    from datetime import date

    # Load models from overlay
    path = os.path.join(os.path.dirname(os.path.dirname(INPUT_DIR)), "input", "project", "models.py")
    spec = importlib.util.spec_from_file_location("models", path)
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)

    book = models.Book(
        title="Test", author="Auth", isbn="978-0000000001",
        published_date=date(2020, 1, 1), genre="Fiction", pages=100,
    )
    # Monkey-patch the import
    fixed_serializers.Book = models.Book
    result = fixed_serializers.serialize_book(book)
    assert result["published_date"] == "2020-01-01"


def test_normalize_removed_or_fixed(output_files):
    """The buggy _normalize_date_value should be fixed or removed."""
    content = _read_file(os.path.join(OUTPUT_DIR, "serializers.py"))
    if content is None:
        pytest.skip("serializers.py not in output")
    # The original bug converts date objects to strings via str()
    # Check that the buggy pattern is gone
    assert "return str(value)" not in content or "hasattr" not in content, (
        "The buggy _normalize_date_value pattern still exists"
    )


def test_format_date_does_not_crash_on_none(fixed_serializers):
    """Edge case: None should not cause an unhandled crash."""
    try:
        result = fixed_serializers._format_date(None)
        # Any non-crash result is acceptable
    except (TypeError, ValueError, AttributeError) as e:
        # TypeError or ValueError is fine (explicit error), AttributeError is not
        if "isoformat" in str(e):
            pytest.fail("_format_date still has the isoformat-on-string bug pattern")


# ===========================================================================
# SECTION 3: Full project tests pass (10 tests via subprocess)
# ===========================================================================

def _run_project_tests(overlay_dir):
    """Run the project's own test suite and return (returncode, output)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "project/tests/", "-v", "--tb=short"],
        cwd=overlay_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


def test_all_original_tests_pass(overlay_dir):
    """The project's own test suite must pass with the fix applied."""
    rc, output = _run_project_tests(overlay_dir)
    assert rc == 0, f"Project tests failed:\n{output}"


def test_test_create_book_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "test_create_book PASSED" in output or "test_create_book" not in output.split("FAILED")


def test_test_list_books_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_list_books" not in output


def test_test_get_book_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_get_book" not in output


def test_test_serialize_book_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_models.py::test_serialize_book" not in output


def test_test_serialize_roundtrip_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_models.py::test_serialize_roundtrip" not in output


def test_test_filter_by_author_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_filter_by_author" not in output


def test_test_filter_by_genre_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_filter_by_genre" not in output


def test_test_duplicate_isbn_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_duplicate_isbn" not in output


def test_test_delete_book_passes(overlay_dir):
    rc, output = _run_project_tests(overlay_dir)
    assert "FAILED project/tests/test_api.py::test_delete_book" not in output


# ===========================================================================
# SECTION 4: API behavior with fixed code (10 tests)
# ===========================================================================

@pytest.fixture(scope="module")
def api_module(overlay_dir):
    """Load the fixed api_handlers module."""
    sys.path.insert(0, overlay_dir)
    spec = importlib.util.spec_from_file_location(
        "project.api_handlers",
        os.path.join(overlay_dir, "project", "api_handlers.py"),
        submodule_search_locations=[os.path.join(overlay_dir, "project")],
    )
    # We need to load the full package
    pkg_spec = importlib.util.spec_from_file_location(
        "project",
        os.path.join(overlay_dir, "project", "__init__.py"),
        submodule_search_locations=[os.path.join(overlay_dir, "project")],
    )
    pkg = importlib.util.module_from_spec(pkg_spec)
    sys.modules["project"] = pkg
    pkg_spec.loader.exec_module(pkg)

    # Load submodules in order
    for submod in ["config", "models", "utils", "validators", "serializers", "database", "middleware", "api_handlers", "routes"]:
        sub_path = os.path.join(overlay_dir, "project", f"{submod}.py")
        if os.path.exists(sub_path):
            sub_spec = importlib.util.spec_from_file_location(f"project.{submod}", sub_path)
            sub = importlib.util.module_from_spec(sub_spec)
            sys.modules[f"project.{submod}"] = sub
            sub_spec.loader.exec_module(sub)

    api = sys.modules["project.api_handlers"]
    api.reset_db()
    return api


def test_api_create_and_retrieve(api_module):
    api_module.reset_db()
    result = api_module.handle_create_book({
        "title": "Dune", "author": "Frank Herbert",
        "isbn": "978-0441172719", "published_date": "1965-08-01",
        "genre": "Fiction", "pages": 412,
    })
    assert result["status"] == 201
    book_id = result["data"]["id"]
    get_result = api_module.handle_get_book(book_id)
    assert get_result["status"] == 200
    assert get_result["data"]["published_date"] == "1965-08-01"


def test_api_list_books(api_module):
    api_module.reset_db()
    api_module.handle_create_book({
        "title": "Book A", "author": "Auth A", "isbn": "978-0000000010",
        "published_date": "2020-01-01",
    })
    api_module.handle_create_book({
        "title": "Book B", "author": "Auth B", "isbn": "978-0000000011",
        "published_date": "2021-06-15",
    })
    result = api_module.handle_list_books()
    assert result["status"] == 200
    assert result["count"] == 2
    dates = [b["published_date"] for b in result["data"]]
    assert "2020-01-01" in dates
    assert "2021-06-15" in dates


def test_api_get_book(api_module):
    api_module.reset_db()
    created = api_module.handle_create_book({
        "title": "1984", "author": "George Orwell", "isbn": "978-0451524935",
        "published_date": "1949-06-08",
    })
    book_id = created["data"]["id"]
    result = api_module.handle_get_book(book_id)
    assert result["status"] == 200
    assert result["data"]["title"] == "1984"


def test_api_create_book(api_module):
    api_module.reset_db()
    result = api_module.handle_create_book({
        "title": "New Book", "author": "New Author", "isbn": "978-0000000012",
        "published_date": "2024-03-15", "genre": "Technology", "pages": 250,
    })
    assert result["status"] == 201
    assert result["data"]["genre"] == "Technology"
    assert result["data"]["pages"] == 250


def test_api_error_handling_missing_fields(api_module):
    result = api_module.handle_create_book({})
    assert result["status"] == 400
    assert len(result["errors"]) >= 3


def test_api_error_handling_invalid_isbn(api_module):
    result = api_module.handle_create_book({
        "title": "Bad", "author": "Auth", "isbn": "invalid",
        "published_date": "2020-01-01",
    })
    assert result["status"] == 400


def test_api_delete_and_verify(api_module):
    api_module.reset_db()
    created = api_module.handle_create_book({
        "title": "Delete Me", "author": "Auth", "isbn": "978-0000000013",
        "published_date": "2020-01-01",
    })
    book_id = created["data"]["id"]
    del_result = api_module.handle_delete_book(book_id)
    assert del_result["status"] == 204
    get_result = api_module.handle_get_book(book_id)
    assert get_result["status"] == 404


def test_api_get_nonexistent(api_module):
    result = api_module.handle_get_book("no-such-id")
    assert result["status"] == 404


def test_api_multiple_books_dates(api_module):
    """All books preserve correct date serialization."""
    api_module.reset_db()
    dates = ["2000-01-01", "2010-06-15", "2023-12-31"]
    for i, d in enumerate(dates):
        api_module.handle_create_book({
            "title": f"Book {i}", "author": "Auth",
            "isbn": f"978-000000{i:04d}", "published_date": d,
        })
    result = api_module.handle_list_books()
    result_dates = sorted([b["published_date"] for b in result["data"]])
    assert result_dates == sorted(dates)


def test_api_date_format_is_iso(api_module):
    """Dates must be in YYYY-MM-DD ISO format."""
    api_module.reset_db()
    created = api_module.handle_create_book({
        "title": "ISO Test", "author": "Auth", "isbn": "978-0000000099",
        "published_date": "2023-07-04",
    })
    import re
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", created["data"]["published_date"])
