# Task 101: Multi-File Refactor from Monolith

## Objective

Refactor the provided monolithic Python file (`input/monolith.py`) into a proper Python package structure with clean separation of concerns. The refactored code MUST produce **identical behavior** to the original monolith.

## Input

You are given `input/monolith.py` — a ~200-line monolithic Python file that handles user registration with:
- Data classes for User and RegistrationRequest
- Email validation logic
- Password strength validation and hashing
- In-memory database operations (CRUD)
- JSON API request/response handling

## Required Output Files

You must produce exactly these 5 files:

### 1. `models.py`
- `User` dataclass with fields: `id`, `email`, `username`, `password_hash`, `created_at`, `is_active`
- `RegistrationRequest` dataclass with fields: `email`, `username`, `password`
- `RegistrationResponse` dataclass with fields: `success`, `message`, `user_id`
- `APIResponse` dataclass with fields: `status_code`, `body`

### 2. `validators.py`
- `validate_email(email: str) -> tuple[bool, str]` — returns (is_valid, error_message)
- `validate_password(password: str) -> tuple[bool, str]` — checks length >= 8, has uppercase, lowercase, digit, special char
- `validate_username(username: str) -> tuple[bool, str]` — checks length 3-20, alphanumeric + underscore only, not starting with digit

### 3. `database.py`
- `UserDatabase` class with an in-memory store
- Methods: `add_user(user) -> bool`, `get_user(user_id) -> User | None`, `get_user_by_email(email) -> User | None`, `get_user_by_username(username) -> User | None`, `delete_user(user_id) -> bool`, `list_users() -> list[User]`, `update_user(user_id, **kwargs) -> User | None`

### 4. `api.py`
- `register_user(request_json: str, db: UserDatabase) -> str` — parses JSON, validates, creates user, returns JSON response
- `get_user_endpoint(user_id: str, db: UserDatabase) -> str` — returns user as JSON
- `delete_user_endpoint(user_id: str, db: UserDatabase) -> str` — deletes user, returns JSON
- `list_users_endpoint(db: UserDatabase) -> str` — lists all users as JSON

### 5. `__init__.py`
- Must export all public classes and functions from the above modules
- Importing from the package directly must work (e.g., `from package import User, validate_email`)

## Constraints

- The refactored modules must use the same hashing logic (SHA-256 with salt) as the monolith
- All JSON responses must be byte-for-byte identical to the monolith for the same inputs
- No external dependencies — only Python standard library
- Each file must be at least 10 lines
- Password hashing must use the same salt generation (first 8 chars of hex digest of email)

## Scoring

**Binary**: ALL tests must pass or score is 0. Tests verify:
- Each module exists and is importable
- Each function/class exists in the correct module
- Integration tests comparing monolith output vs refactored output for identical inputs
- Edge cases in validation, database operations, and API responses
