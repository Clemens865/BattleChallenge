# Task: Email Validation Function

## Requirements

Create a Python module `validate_email.py` that exports a function `validate_email(email: str) -> bool`.

The function should return `True` for valid email addresses and `False` for invalid ones.

### Rules

1. Must contain exactly one `@` symbol
2. Local part (before @) must be 1-64 characters
3. Domain part (after @) must be 1-255 characters
4. Domain must contain at least one `.`
5. Domain parts must be alphanumeric (hyphens allowed, not at start/end)
6. Local part allows: letters, digits, `.`, `_`, `-`, `+`
7. No consecutive dots in local part
8. Cannot start or end with a dot in local part

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Function handles edge cases correctly
- No external dependencies (stdlib only)
