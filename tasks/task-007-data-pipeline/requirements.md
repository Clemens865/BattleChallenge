# Task: Multi-Step Data Transformation Pipeline

## Requirements

Create a Python module `pipeline.py` that implements a configurable data transformation pipeline.

### `Pipeline` Class

```python
class Pipeline:
    def __init__(self):
        """Initialize an empty pipeline."""

    def add_step(self, name: str, transform_fn: callable) -> "Pipeline":
        """Add a named transformation step. Returns self for chaining.
        transform_fn takes a list of dicts and returns a list of dicts."""

    def run(self, data: list[dict]) -> list[dict]:
        """Execute all steps in order on the input data. Returns transformed data."""

    def run_with_trace(self, data: list[dict]) -> dict:
        """Execute all steps and return a trace dict with:
        - 'result': final transformed data
        - 'steps': list of dicts with 'name', 'input_count', 'output_count', 'duration_ms'
        - 'total_duration_ms': total time in milliseconds
        """

    def remove_step(self, name: str) -> "Pipeline":
        """Remove a step by name. Raises ValueError if not found. Returns self."""
```

### Built-in Transform Functions

The module must also export these ready-made transform functions:

```python
def filter_rows(key: str, condition: callable) -> callable:
    """Returns a transform that filters rows where condition(row[key]) is True."""

def map_column(key: str, transform: callable) -> callable:
    """Returns a transform that applies transform() to each row's key value."""

def add_column(key: str, compute: callable) -> callable:
    """Returns a transform that adds a new column computed from each row."""

def sort_by(key: str, reverse: bool = False) -> callable:
    """Returns a transform that sorts rows by the given key."""

def deduplicate(key: str) -> callable:
    """Returns a transform that removes duplicate rows based on a key."""
```

## Example Usage

```python
p = Pipeline()
p.add_step("filter_adults", filter_rows("age", lambda x: x >= 18))
p.add_step("add_label", add_column("label", lambda row: f"{row['name']} ({row['age']})"))
p.add_step("sort", sort_by("age"))
result = p.run(data)
```

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Pipeline steps execute in insertion order
- No external dependencies (stdlib only)
