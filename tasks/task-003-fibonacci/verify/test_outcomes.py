"""Outcome-based tests for Fibonacci task."""
import importlib.util
import os
import pytest


def load_solution():
    """Load fibonacci module from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "fibonacci.py")
    if not os.path.exists(module_path):
        pytest.skip(f"fibonacci.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("fibonacci", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fib():
    return load_solution().fib


@pytest.fixture
def fib_sequence():
    return load_solution().fib_sequence


@pytest.fixture
def is_fibonacci():
    return load_solution().is_fibonacci


# --- fib(n) tests ---

def test_fib_zero(fib):
    assert fib(0) == 0

def test_fib_one(fib):
    assert fib(1) == 1

def test_fib_small(fib):
    assert fib(5) == 5

def test_fib_ten(fib):
    assert fib(10) == 55

def test_fib_twenty(fib):
    assert fib(20) == 6765

def test_fib_large(fib):
    assert fib(50) == 12586269025

def test_fib_negative_raises(fib):
    with pytest.raises(ValueError):
        fib(-1)


# --- fib_sequence(n) tests ---

def test_sequence_empty(fib_sequence):
    assert fib_sequence(0) == []

def test_sequence_one(fib_sequence):
    assert fib_sequence(1) == [0]

def test_sequence_two(fib_sequence):
    assert fib_sequence(2) == [0, 1]

def test_sequence_five(fib_sequence):
    assert fib_sequence(5) == [0, 1, 1, 2, 3]

def test_sequence_ten(fib_sequence):
    assert fib_sequence(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

def test_sequence_negative_raises(fib_sequence):
    with pytest.raises(ValueError):
        fib_sequence(-5)


# --- is_fibonacci(num) tests ---

def test_is_fib_zero(is_fibonacci):
    assert is_fibonacci(0) is True

def test_is_fib_one(is_fibonacci):
    assert is_fibonacci(1) is True

def test_is_fib_thirteen(is_fibonacci):
    assert is_fibonacci(13) is True

def test_is_fib_twenty_one(is_fibonacci):
    assert is_fibonacci(21) is True

def test_is_not_fib_four(is_fibonacci):
    assert is_fibonacci(4) is False

def test_is_not_fib_ten(is_fibonacci):
    assert is_fibonacci(10) is False

def test_is_not_fib_large(is_fibonacci):
    assert is_fibonacci(100) is False

def test_is_fib_negative_raises(is_fibonacci):
    with pytest.raises(ValueError):
        is_fibonacci(-3)
