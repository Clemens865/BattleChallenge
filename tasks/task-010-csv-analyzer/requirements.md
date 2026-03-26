# Task: CSV Data Analyzer

## Requirements

Create a Python module `csv_analyzer.py` that reads CSV files and performs statistical analysis and data queries.

### `CSVAnalyzer` Class

```python
class CSVAnalyzer:
    def __init__(self, filepath: str):
        """Load a CSV file. First row is treated as headers.
        Raises FileNotFoundError if file doesn't exist.
        """

    def columns(self) -> list[str]:
        """Return list of column names."""

    def row_count(self) -> int:
        """Return number of data rows (excluding header)."""

    def describe(self, column: str) -> dict:
        """Return statistics for a numeric column:
        - 'count': number of non-empty values
        - 'mean': arithmetic mean
        - 'min': minimum value
        - 'max': maximum value
        - 'sum': sum of values
        - 'std': population standard deviation
        Raises ValueError if column doesn't exist or is not numeric.
        """

    def value_counts(self, column: str) -> dict:
        """Return a dict mapping each unique value in the column to its count.
        Sorted by count descending.
        Raises ValueError if column doesn't exist.
        """

    def filter_rows(self, column: str, operator: str, value) -> list[dict]:
        """Filter rows where column satisfies the condition.
        Supported operators: '==', '!=', '>', '<', '>=', '<=', 'contains'
        - For numeric columns, comparisons are numeric
        - 'contains' does case-insensitive substring match
        Returns list of row dicts.
        Raises ValueError if column doesn't exist or operator is invalid.
        """

    def group_by(self, column: str, agg_column: str, agg_func: str) -> dict:
        """Group rows by column, aggregate agg_column.
        agg_func: 'sum', 'mean', 'count', 'min', 'max'
        Returns dict mapping group values to aggregated results.
        Raises ValueError for invalid column or function.
        """

    def to_dict_list(self) -> list[dict]:
        """Return all rows as a list of dicts."""

    def export(self, filepath: str, rows: list[dict] = None) -> None:
        """Export data to CSV file. If rows provided, export those; otherwise export all data."""
```

## Acceptance Criteria

- All test cases in `verify/test_outcomes.py` pass
- Numeric detection should handle integers and floats
- No external dependencies (stdlib only, use csv module)
