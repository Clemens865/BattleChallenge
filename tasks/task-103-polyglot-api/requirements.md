# Task 103: Polyglot Key-Value Store

## Objective

Build a key-value store system with a Python server and BOTH a Python client library AND a TypeScript client library. All three components communicate via a shared JSON-line protocol over stdin/stdout.

## Required Output Files

### 1. `server.py`
A KV store server that reads JSON commands from stdin and writes JSON responses to stdout (one JSON object per line).

Supported operations:
- **SET**: `{"op": "SET", "key": "...", "value": "...", "ttl": null|seconds}` -> `{"ok": true}`
- **GET**: `{"op": "GET", "key": "..."}` -> `{"ok": true, "value": "..."}` or `{"ok": false, "error": "NOT_FOUND"}`
- **DELETE**: `{"op": "DELETE", "key": "..."}` -> `{"ok": true, "deleted": true}` or `{"ok": false, "error": "NOT_FOUND"}`
- **LIST**: `{"op": "LIST", "prefix": "..."|null}` -> `{"ok": true, "keys": [...]}`
- **EXPIRE**: `{"op": "EXPIRE", "key": "...", "ttl": seconds}` -> `{"ok": true}` or `{"ok": false, "error": "NOT_FOUND"}`
- **PING**: `{"op": "PING"}` -> `{"ok": true, "pong": true}`
- Unknown operations -> `{"ok": false, "error": "UNKNOWN_OP"}`

TTL behavior:
- Keys with expired TTL must not be returned by GET or LIST
- TTL is in seconds from the time of SET or EXPIRE
- Setting TTL to null or 0 means no expiry
- DELETE on an expired key returns NOT_FOUND

### 2. `client.py`
A Python client class `KVClient` that:
- Spawns the server as a subprocess
- Provides methods: `set(key, value, ttl=None)`, `get(key)`, `delete(key)`, `list(prefix=None)`, `expire(key, ttl)`, `ping()`, `close()`
- `get()` returns `None` if key not found
- `list()` returns a list of key strings
- Must handle server process lifecycle (start/stop)

### 3. `client.ts`
A TypeScript client class `KVClient` that:
- Spawns the server as a child process
- Provides the same methods as the Python client
- Uses async/await pattern
- Properly handles stdin/stdout buffering (newline-delimited JSON)

### 4. `protocol.md`
Documentation of the JSON protocol including:
- Message format specification
- All operation types with request/response examples
- Error codes and their meanings
- TTL behavior specification

## Constraints

- Server must handle malformed JSON gracefully (return error, don't crash)
- Keys can contain any printable ASCII characters except newline
- Values can be any valid JSON string (including unicode, escaped chars)
- No external dependencies for server.py and client.py (standard library only)
- TypeScript client may use Node.js built-in modules only (child_process, readline)
- Each file must be at least 10 lines

## Scoring

**Binary**: ALL tests must pass or score is 0. Tests include:
- Basic CRUD operations via Python client
- TTL/expiry behavior
- Cross-language interop (Python sets, TypeScript gets)
- Protocol error handling
- Special characters in keys and values
- Large values (10KB+)
- Prefix-filtered listing
- Server graceful shutdown
