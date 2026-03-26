"""Outcome-based tests for task-103: Polyglot key-value store."""
import importlib.util
import json
import os
import subprocess
import sys
import time
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _load_module(name, filename=None):
    filename = filename or f"{name}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found in {OUTPUT_DIR}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(scope="module")
def server_mod():
    return _load_module("server")


@pytest.fixture(scope="module")
def client_mod():
    return _load_module("client")


class ServerProcess:
    """Manage a server subprocess for testing."""

    def __init__(self):
        server_path = os.path.join(OUTPUT_DIR, "server.py")
        self.proc = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def send(self, obj: dict) -> dict:
        line = json.dumps(obj) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        resp_line = self.proc.stdout.readline()
        if not resp_line:
            raise RuntimeError("Server closed stdout")
        return json.loads(resp_line.strip())

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


@pytest.fixture
def server():
    srv = ServerProcess()
    yield srv
    srv.close()


@pytest.fixture
def kv_client(client_mod):
    """Create a KVClient instance from the submitted client module."""
    client = client_mod.KVClient(server_cmd=[sys.executable, os.path.join(OUTPUT_DIR, "server.py")])
    yield client
    try:
        client.close()
    except Exception:
        pass


# ===========================================================================
# SECTION 1: File existence (4 tests)
# ===========================================================================

REQUIRED_FILES = ["server.py", "client.py", "client.ts", "protocol.md"]


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
    assert len(lines) >= 10, f"{filename} has only {len(lines)} lines"


# ===========================================================================
# SECTION 2: Raw server protocol (10 tests)
# ===========================================================================

def test_server_ping(server):
    resp = server.send({"op": "PING"})
    assert resp["ok"] is True
    assert resp.get("pong") is True


def test_server_set_get(server):
    server.send({"op": "SET", "key": "foo", "value": "bar"})
    resp = server.send({"op": "GET", "key": "foo"})
    assert resp["ok"] is True
    assert resp["value"] == "bar"


def test_server_get_missing(server):
    resp = server.send({"op": "GET", "key": "nonexistent"})
    assert resp["ok"] is False
    assert resp["error"] == "NOT_FOUND"


def test_server_delete(server):
    server.send({"op": "SET", "key": "del_me", "value": "val"})
    resp = server.send({"op": "DELETE", "key": "del_me"})
    assert resp["ok"] is True
    assert resp["deleted"] is True
    resp2 = server.send({"op": "GET", "key": "del_me"})
    assert resp2["ok"] is False


def test_server_delete_missing(server):
    resp = server.send({"op": "DELETE", "key": "nope"})
    assert resp["ok"] is False
    assert resp["error"] == "NOT_FOUND"


def test_server_list(server):
    server.send({"op": "SET", "key": "list_a", "value": "1"})
    server.send({"op": "SET", "key": "list_b", "value": "2"})
    resp = server.send({"op": "LIST", "prefix": "list_"})
    assert resp["ok"] is True
    assert set(resp["keys"]) >= {"list_a", "list_b"}


def test_server_list_no_prefix(server):
    server.send({"op": "SET", "key": "any_key", "value": "v"})
    resp = server.send({"op": "LIST", "prefix": None})
    assert resp["ok"] is True
    assert "any_key" in resp["keys"]


def test_server_unknown_op(server):
    resp = server.send({"op": "FOOBAR"})
    assert resp["ok"] is False
    assert resp["error"] == "UNKNOWN_OP"


def test_server_malformed_json():
    """Server must not crash on malformed JSON."""
    server_path = os.path.join(OUTPUT_DIR, "server.py")
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        proc.stdin.write("this is not json\n")
        proc.stdin.flush()
        resp_line = proc.stdout.readline()
        resp = json.loads(resp_line.strip())
        assert resp["ok"] is False
        # Server should still be alive — send a valid command
        proc.stdin.write(json.dumps({"op": "PING"}) + "\n")
        proc.stdin.flush()
        resp2_line = proc.stdout.readline()
        resp2 = json.loads(resp2_line.strip())
        assert resp2["ok"] is True
    finally:
        proc.stdin.close()
        proc.kill()


def test_server_overwrite_key(server):
    server.send({"op": "SET", "key": "ow", "value": "v1"})
    server.send({"op": "SET", "key": "ow", "value": "v2"})
    resp = server.send({"op": "GET", "key": "ow"})
    assert resp["value"] == "v2"


# ===========================================================================
# SECTION 3: TTL / Expire (5 tests)
# ===========================================================================

def test_server_set_with_ttl(server):
    server.send({"op": "SET", "key": "ttl1", "value": "val", "ttl": 10})
    resp = server.send({"op": "GET", "key": "ttl1"})
    assert resp["ok"] is True


def test_server_ttl_expiry(server):
    server.send({"op": "SET", "key": "ttl_exp", "value": "val", "ttl": 1})
    time.sleep(1.5)
    resp = server.send({"op": "GET", "key": "ttl_exp"})
    assert resp["ok"] is False
    assert resp["error"] == "NOT_FOUND"


def test_server_expire_command(server):
    server.send({"op": "SET", "key": "exp1", "value": "val"})
    resp = server.send({"op": "EXPIRE", "key": "exp1", "ttl": 1})
    assert resp["ok"] is True
    time.sleep(1.5)
    resp2 = server.send({"op": "GET", "key": "exp1"})
    assert resp2["ok"] is False


def test_server_expire_missing_key(server):
    resp = server.send({"op": "EXPIRE", "key": "nokey", "ttl": 5})
    assert resp["ok"] is False
    assert resp["error"] == "NOT_FOUND"


def test_server_expired_not_in_list(server):
    server.send({"op": "SET", "key": "list_ttl_a", "value": "v", "ttl": 1})
    server.send({"op": "SET", "key": "list_ttl_b", "value": "v"})
    time.sleep(1.5)
    resp = server.send({"op": "LIST", "prefix": "list_ttl_"})
    assert "list_ttl_a" not in resp["keys"]
    assert "list_ttl_b" in resp["keys"]


# ===========================================================================
# SECTION 4: Python client (5 tests)
# ===========================================================================

def test_client_set_get(kv_client):
    kv_client.set("ck1", "cv1")
    assert kv_client.get("ck1") == "cv1"


def test_client_get_none(kv_client):
    assert kv_client.get("missing_key_xyz") is None


def test_client_delete(kv_client):
    kv_client.set("cdel", "val")
    result = kv_client.delete("cdel")
    assert result is True
    assert kv_client.get("cdel") is None


def test_client_list(kv_client):
    kv_client.set("cl_a", "1")
    kv_client.set("cl_b", "2")
    keys = kv_client.list(prefix="cl_")
    assert isinstance(keys, list)
    assert "cl_a" in keys and "cl_b" in keys


def test_client_ping(kv_client):
    result = kv_client.ping()
    assert result is True


# ===========================================================================
# SECTION 5: Edge cases (6 tests)
# ===========================================================================

def test_special_chars_in_key(server):
    server.send({"op": "SET", "key": "key with spaces!@#$%", "value": "ok"})
    resp = server.send({"op": "GET", "key": "key with spaces!@#$%"})
    assert resp["value"] == "ok"


def test_unicode_value(server):
    server.send({"op": "SET", "key": "uni", "value": "Hello \u00e9\u00e8\u00ea \u2603 \ud83d\ude00"})
    resp = server.send({"op": "GET", "key": "uni"})
    assert "\u2603" in resp["value"]


def test_large_value(server):
    big = "x" * 10000
    server.send({"op": "SET", "key": "bigval", "value": big})
    resp = server.send({"op": "GET", "key": "bigval"})
    assert resp["value"] == big


def test_empty_value(server):
    server.send({"op": "SET", "key": "empty_val", "value": ""})
    resp = server.send({"op": "GET", "key": "empty_val"})
    assert resp["ok"] is True
    assert resp["value"] == ""


def test_empty_prefix_list(server):
    """LIST with empty string prefix returns all keys."""
    server.send({"op": "SET", "key": "z_test", "value": "1"})
    resp = server.send({"op": "LIST", "prefix": ""})
    assert resp["ok"] is True
    assert "z_test" in resp["keys"]


def test_delete_expired_returns_not_found(server):
    server.send({"op": "SET", "key": "del_exp", "value": "v", "ttl": 1})
    time.sleep(1.5)
    resp = server.send({"op": "DELETE", "key": "del_exp"})
    assert resp["ok"] is False
    assert resp["error"] == "NOT_FOUND"


# ===========================================================================
# SECTION 6: TypeScript client file validity (2 tests)
# ===========================================================================

def test_ts_client_has_class():
    path = os.path.join(OUTPUT_DIR, "client.ts")
    if not os.path.isfile(path):
        pytest.skip("client.ts not found")
    with open(path) as f:
        content = f.read()
    assert "class KVClient" in content or "export class KVClient" in content


def test_ts_client_has_methods():
    path = os.path.join(OUTPUT_DIR, "client.ts")
    if not os.path.isfile(path):
        pytest.skip("client.ts not found")
    with open(path) as f:
        content = f.read()
    for method in ["get(", "set(", "delete(", "list(", "close("]:
        assert method in content, f"client.ts missing method: {method}"


# ===========================================================================
# SECTION 7: Protocol documentation (2 tests)
# ===========================================================================

def test_protocol_md_has_operations():
    path = os.path.join(OUTPUT_DIR, "protocol.md")
    if not os.path.isfile(path):
        pytest.skip("protocol.md not found")
    with open(path) as f:
        content = f.read().upper()
    for op in ["SET", "GET", "DELETE", "LIST", "EXPIRE", "PING"]:
        assert op in content, f"protocol.md missing operation: {op}"


def test_protocol_md_has_error_codes():
    path = os.path.join(OUTPUT_DIR, "protocol.md")
    if not os.path.isfile(path):
        pytest.skip("protocol.md not found")
    with open(path) as f:
        content = f.read()
    assert "NOT_FOUND" in content
    assert "UNKNOWN_OP" in content
