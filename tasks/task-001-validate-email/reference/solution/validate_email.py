"""Reference implementation for email validation."""
import re


def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False

    if email.count("@") != 1:
        return False

    local, domain = email.split("@")

    if not local or len(local) > 64:
        return False
    if not domain or len(domain) > 255:
        return False

    # Local part rules
    if local.startswith(".") or local.endswith("."):
        return False
    if ".." in local:
        return False
    if not re.match(r'^[a-zA-Z0-9._+\-]+$', local):
        return False

    # Domain rules
    if "." not in domain:
        return False
    parts = domain.split(".")
    for part in parts:
        if not part:
            return False
        if part.startswith("-") or part.endswith("-"):
            return False
        if not re.match(r'^[a-zA-Z0-9\-]+$', part):
            return False

    return True
