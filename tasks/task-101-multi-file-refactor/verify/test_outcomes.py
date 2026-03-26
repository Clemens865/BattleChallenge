"""Outcome-based tests for task-101: Multi-file refactor from monolith."""
import importlib.util
import json
import os
import sys
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())
TASK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(TASK_DIR, "input")


def _load_module(name, filename=None):
    """Dynamically load a module from OUTPUT_DIR."""
    filename = filename or f"{name}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found in {OUTPUT_DIR}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_monolith():
    path = os.path.join(INPUT_DIR, "monolith.py")
    spec = importlib.util.spec_from_file_location("monolith", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def monolith():
    return _load_monolith()


@pytest.fixture(scope="module")
def models():
    return _load_module("models")


@pytest.fixture(scope="module")
def validators():
    return _load_module("validators")


@pytest.fixture(scope="module")
def database():
    return _load_module("database")


@pytest.fixture(scope="module")
def api():
    return _load_module("api")


@pytest.fixture(scope="module")
def init_mod():
    """Load __init__.py as a package proxy."""
    return _load_module("pkg_init", "__init__.py")


# ===========================================================================
# SECTION 1: File existence & minimum line counts (5 tests)
# ===========================================================================

REQUIRED_FILES = ["models.py", "validators.py", "database.py", "api.py", "__init__.py"]


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_file_exists(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    assert os.path.isfile(path), f"{filename} not found"


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_file_min_lines(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(path):
        pytest.skip(f"{filename} not found")
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) >= 10, f"{filename} has only {len(lines)} lines (need >=10)"


# ===========================================================================
# SECTION 2: Models module (4 tests)
# ===========================================================================

def test_models_has_user(models):
    assert hasattr(models, "User"), "models.py must export User"


def test_models_has_registration_request(models):
    assert hasattr(models, "RegistrationRequest")


def test_models_has_registration_response(models):
    assert hasattr(models, "RegistrationResponse")


def test_models_has_api_response(models):
    assert hasattr(models, "APIResponse")


# ===========================================================================
# SECTION 3: Validators module (6 tests)
# ===========================================================================

def test_validators_has_validate_email(validators):
    assert callable(getattr(validators, "validate_email", None))


def test_validators_has_validate_password(validators):
    assert callable(getattr(validators, "validate_password", None))


def test_validators_has_validate_username(validators):
    assert callable(getattr(validators, "validate_username", None))


def test_validate_email_valid(validators):
    ok, msg = validators.validate_email("user@example.com")
    assert ok is True


def test_validate_email_invalid(validators):
    ok, msg = validators.validate_email("not-an-email")
    assert ok is False
    assert isinstance(msg, str) and len(msg) > 0


def test_validate_password_weak(validators):
    ok, msg = validators.validate_password("short")
    assert ok is False


def test_validate_password_strong(validators):
    ok, msg = validators.validate_password("Str0ng!Pass")
    assert ok is True


def test_validate_username_starts_with_digit(validators):
    ok, msg = validators.validate_username("1badname")
    assert ok is False


def test_validate_username_valid(validators):
    ok, msg = validators.validate_username("good_name")
    assert ok is True


# ===========================================================================
# SECTION 4: Database module (6 tests)
# ===========================================================================

def test_database_has_class(database):
    assert hasattr(database, "UserDatabase")


def _make_user(models, email="a@b.com", username="alice"):
    import uuid
    return models.User(
        id=str(uuid.uuid4()),
        email=email,
        username=username,
        password_hash="abc123",
        created_at="2026-01-01T00:00:00+00:00",
    )


def test_database_add_and_get(database, models):
    db = database.UserDatabase()
    user = _make_user(models)
    assert db.add_user(user) is True
    assert db.get_user(user.id) is not None


def test_database_duplicate_add(database, models):
    db = database.UserDatabase()
    user = _make_user(models)
    db.add_user(user)
    assert db.add_user(user) is False


def test_database_get_by_email(database, models):
    db = database.UserDatabase()
    user = _make_user(models, email="find@me.com")
    db.add_user(user)
    found = db.get_user_by_email("find@me.com")
    assert found is not None and found.email == "find@me.com"


def test_database_delete(database, models):
    db = database.UserDatabase()
    user = _make_user(models)
    db.add_user(user)
    assert db.delete_user(user.id) is True
    assert db.get_user(user.id) is None


def test_database_list_users(database, models):
    db = database.UserDatabase()
    u1 = _make_user(models, email="x@y.com", username="ux")
    u2 = _make_user(models, email="a@b.com", username="ua")
    db.add_user(u1)
    db.add_user(u2)
    assert len(db.list_users()) == 2


def test_database_update_user(database, models):
    db = database.UserDatabase()
    user = _make_user(models, email="upd@te.com", username="upd")
    db.add_user(user)
    updated = db.update_user(user.id, is_active=False)
    assert updated is not None
    assert updated.is_active is False


# ===========================================================================
# SECTION 5: API module — existence (4 tests)
# ===========================================================================

def test_api_has_register_user(api):
    assert callable(getattr(api, "register_user", None))


def test_api_has_get_user_endpoint(api):
    assert callable(getattr(api, "get_user_endpoint", None))


def test_api_has_delete_user_endpoint(api):
    assert callable(getattr(api, "delete_user_endpoint", None))


def test_api_has_list_users_endpoint(api):
    assert callable(getattr(api, "list_users_endpoint", None))


# ===========================================================================
# SECTION 6: __init__.py exports (2 tests)
# ===========================================================================

def test_init_exports_models(init_mod):
    for name in ("User", "RegistrationRequest", "RegistrationResponse", "APIResponse"):
        assert hasattr(init_mod, name), f"__init__.py must export {name}"


def test_init_exports_validators(init_mod):
    for name in ("validate_email", "validate_password", "validate_username"):
        assert hasattr(init_mod, name), f"__init__.py must export {name}"


# ===========================================================================
# SECTION 7: Integration — identical behavior to monolith (8 tests)
# ===========================================================================

def _get_db_pair(monolith, database):
    """Return a (monolith_db, refactored_db) pair."""
    return monolith.UserDatabase(), database.UserDatabase()


def _register_json(email, username, password):
    return json.dumps({"email": email, "username": username, "password": password})


def test_integration_register_success(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("int@test.com", "intuser", "P@ssw0rd!")
    m_resp = monolith.register_user(req, m_db)
    r_resp = api.register_user(req, r_db)
    # Both must parse as identical JSON (sort_keys guarantees order)
    assert json.loads(m_resp) == json.loads(r_resp)


def test_integration_register_bad_email(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("bad-email", "user1", "P@ssw0rd!")
    assert json.loads(monolith.register_user(req, m_db)) == json.loads(api.register_user(req, r_db))


def test_integration_register_weak_password(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("ok@ok.com", "user2", "weak")
    assert json.loads(monolith.register_user(req, m_db)) == json.loads(api.register_user(req, r_db))


def test_integration_register_bad_username(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("ok2@ok.com", "1bad", "P@ssw0rd!")
    assert json.loads(monolith.register_user(req, m_db)) == json.loads(api.register_user(req, r_db))


def test_integration_register_invalid_json(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    assert json.loads(monolith.register_user("{bad", m_db)) == json.loads(api.register_user("{bad", r_db))


def test_integration_get_user(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("get@test.com", "getuser", "P@ssw0rd!")
    monolith.register_user(req, m_db)
    api.register_user(req, r_db)
    # Derive the user_id (uuid5 from email)
    import uuid
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "get@test.com"))
    m_resp = json.loads(monolith.get_user_endpoint(uid, m_db))
    r_resp = json.loads(api.get_user_endpoint(uid, r_db))
    # created_at will differ by microseconds; compare structure
    assert m_resp["status_code"] == r_resp["status_code"]
    assert m_resp["body"]["success"] == r_resp["body"]["success"]
    assert m_resp["body"]["user"]["email"] == r_resp["body"]["user"]["email"]


def test_integration_delete_nonexistent(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    assert json.loads(monolith.delete_user_endpoint("fake", m_db)) == json.loads(api.delete_user_endpoint("fake", r_db))


def test_integration_list_empty(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    assert json.loads(monolith.list_users_endpoint(m_db)) == json.loads(api.list_users_endpoint(r_db))


def test_integration_duplicate_email(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("dup@test.com", "dupuser1", "P@ssw0rd!")
    monolith.register_user(req, m_db)
    api.register_user(req, r_db)
    req2 = _register_json("dup@test.com", "dupuser2", "P@ssw0rd!")
    assert json.loads(monolith.register_user(req2, m_db)) == json.loads(api.register_user(req2, r_db))


def test_integration_duplicate_username(monolith, api, database):
    m_db, r_db = _get_db_pair(monolith, database)
    req = _register_json("u1@test.com", "sameuser", "P@ssw0rd!")
    monolith.register_user(req, m_db)
    api.register_user(req, r_db)
    req2 = _register_json("u2@test.com", "sameuser", "P@ssw0rd!")
    assert json.loads(monolith.register_user(req2, m_db)) == json.loads(api.register_user(req2, r_db))


# ===========================================================================
# SECTION 8: Validator edge-case parity with monolith (5 tests)
# ===========================================================================

def test_validate_email_empty_parity(monolith, validators):
    assert monolith.validate_email("") == validators.validate_email("")


def test_validate_email_long_parity(monolith, validators):
    long_email = "a" * 250 + "@b.com"
    assert monolith.validate_email(long_email) == validators.validate_email(long_email)


def test_validate_password_only_upper(monolith, validators):
    assert monolith.validate_password("ALLUPPERCASE") == validators.validate_password("ALLUPPERCASE")


def test_validate_username_too_long(monolith, validators):
    assert monolith.validate_username("a" * 21) == validators.validate_username("a" * 21)


def test_validate_username_special_chars(monolith, validators):
    assert monolith.validate_username("bad-name!") == validators.validate_username("bad-name!")
