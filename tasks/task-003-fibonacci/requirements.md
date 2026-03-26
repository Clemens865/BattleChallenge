# Task: Fibonacci Sequence Generator

## Requirements

Create a Python module `fibonacci.py` that exports the following functions:

### `fib(n: int) -> int`
Returns the nth Fibonacci number (0-indexed).
- `fib(0)` returns `0`
- `fib(1)` returns `1`
- `fib(n)` returns `fib(n-1) + fib(n-2)` for `n >= 2`
- Must raise `ValueError` for negative input

### `fib_sequence(n: int) -> list[int]`
Returns the first `n` Fibonacci numbers as a list.
- `fib_sequence(0)` returns `[]`
- `fib_sequence(1)` returns `[0]`
- `fib_sequence(5)` returns `[0, 1, 1, 2, 3]`
- Must raise `ValueError` for negative input

### `is_fibonacci(num: int) -> bool`
Returns `True` if the given non-negative integer is a Fibonacci number, `False` otherwise.
- Must raise `ValueError` for negative input

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Must handle large values efficiently (up to n=50)
- No external dependencies (stdlib only)
