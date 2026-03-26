"""Outcome-based tests for email validation task."""
import importlib.util
import os
import sys
import pytest


def load_solution():
    """Load validate_email from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "validate_email.py")
    if not os.path.exists(module_path):
        pytest.skip(f"validate_email.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("validate_email", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_email


@pytest.fixture
def validate():
    return load_solution()


# --- Valid emails ---

def test_simple_valid(validate):
    assert validate("user@example.com") is True

def test_subdomain(validate):
    assert validate("user@mail.example.com") is True

def test_plus_addressing(validate):
    assert validate("user+tag@example.com") is True

def test_dots_in_local(validate):
    assert validate("first.last@example.com") is True

def test_hyphen_in_domain(validate):
    assert validate("user@my-domain.com") is True

def test_numeric_local(validate):
    assert validate("123@example.com") is True

def test_underscore_local(validate):
    assert validate("user_name@example.com") is True


# --- Invalid emails ---

def test_no_at(validate):
    assert validate("userexample.com") is False

def test_double_at(validate):
    assert validate("user@@example.com") is False

def test_no_domain_dot(validate):
    assert validate("user@example") is False

def test_empty_local(validate):
    assert validate("@example.com") is False

def test_empty_domain(validate):
    assert validate("user@") is False

def test_leading_dot_local(validate):
    assert validate(".user@example.com") is False

def test_trailing_dot_local(validate):
    assert validate("user.@example.com") is False

def test_consecutive_dots(validate):
    assert validate("user..name@example.com") is False

def test_empty_string(validate):
    assert validate("") is False

def test_space_in_email(validate):
    assert validate("user @example.com") is False

def test_domain_starts_with_hyphen(validate):
    assert validate("user@-example.com") is False
