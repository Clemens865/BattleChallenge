"""Outcome-based tests for CSV analyzer task."""
import importlib.util
import csv
import math
import os
import tempfile
import pytest


def load_solution():
    """Load CSVAnalyzer from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "csv_analyzer.py")
    if not os.path.exists(module_path):
        pytest.skip(f"csv_analyzer.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("csv_analyzer", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CSVAnalyzer


SAMPLE_CSV = """\
name,age,city,salary
Alice,30,NYC,70000
Bob,25,LA,55000
Charlie,35,NYC,85000
Diana,28,Chicago,62000
Eve,30,NYC,70000
Frank,40,LA,95000
Grace,22,Chicago,48000
"""


@pytest.fixture
def csv_path():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        f.write(SAMPLE_CSV)
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def analyzer(csv_path):
    CSVAnalyzer = load_solution()
    return CSVAnalyzer(csv_path)


# --- Basic loading ---

def test_columns(analyzer):
    assert analyzer.columns() == ["name", "age", "city", "salary"]

def test_row_count(analyzer):
    assert analyzer.row_count() == 7

def test_file_not_found():
    CSVAnalyzer = load_solution()
    with pytest.raises(FileNotFoundError):
        CSVAnalyzer("/nonexistent/path.csv")


# --- Describe ---

def test_describe_age(analyzer):
    stats = analyzer.describe("age")
    assert stats["count"] == 7
    assert stats["min"] == 22
    assert stats["max"] == 40
    assert abs(stats["mean"] - 30.0) < 0.01
    assert stats["sum"] == 210

def test_describe_salary(analyzer):
    stats = analyzer.describe("salary")
    assert stats["count"] == 7
    assert stats["min"] == 48000
    assert stats["max"] == 95000

def test_describe_has_std(analyzer):
    stats = analyzer.describe("age")
    assert "std" in stats
    assert stats["std"] > 0

def test_describe_nonexistent_column(analyzer):
    with pytest.raises(ValueError):
        analyzer.describe("nonexistent")

def test_describe_non_numeric_column(analyzer):
    with pytest.raises(ValueError):
        analyzer.describe("name")


# --- Value counts ---

def test_value_counts_city(analyzer):
    counts = analyzer.value_counts("city")
    assert counts["NYC"] == 3
    assert counts["LA"] == 2
    assert counts["Chicago"] == 2

def test_value_counts_sorted_descending(analyzer):
    counts = analyzer.value_counts("city")
    values = list(counts.values())
    assert values == sorted(values, reverse=True)

def test_value_counts_nonexistent_column(analyzer):
    with pytest.raises(ValueError):
        analyzer.value_counts("nonexistent")


# --- Filter ---

def test_filter_equals(analyzer):
    rows = analyzer.filter_rows("city", "==", "NYC")
    assert len(rows) == 3
    assert all(r["city"] == "NYC" for r in rows)

def test_filter_not_equals(analyzer):
    rows = analyzer.filter_rows("city", "!=", "NYC")
    assert len(rows) == 4

def test_filter_greater_than(analyzer):
    rows = analyzer.filter_rows("age", ">", 30)
    assert len(rows) == 2
    assert all(float(r["age"]) > 30 for r in rows)

def test_filter_less_than(analyzer):
    rows = analyzer.filter_rows("salary", "<", 60000)
    assert len(rows) == 2

def test_filter_greater_equal(analyzer):
    rows = analyzer.filter_rows("age", ">=", 30)
    assert len(rows) == 4

def test_filter_contains(analyzer):
    rows = analyzer.filter_rows("name", "contains", "a")
    names = [r["name"] for r in rows]
    assert "Charlie" in names
    assert "Diana" in names
    assert "Grace" in names

def test_filter_invalid_column(analyzer):
    with pytest.raises(ValueError):
        analyzer.filter_rows("nope", "==", "x")

def test_filter_invalid_operator(analyzer):
    with pytest.raises(ValueError):
        analyzer.filter_rows("age", "~=", 5)


# --- Group by ---

def test_group_by_sum(analyzer):
    result = analyzer.group_by("city", "salary", "sum")
    assert result["NYC"] == 225000
    assert result["LA"] == 150000
    assert result["Chicago"] == 110000

def test_group_by_mean(analyzer):
    result = analyzer.group_by("city", "salary", "mean")
    assert abs(result["NYC"] - 75000) < 0.01

def test_group_by_count(analyzer):
    result = analyzer.group_by("city", "age", "count")
    assert result["NYC"] == 3
    assert result["LA"] == 2

def test_group_by_min(analyzer):
    result = analyzer.group_by("city", "age", "min")
    assert result["NYC"] == 30
    assert result["Chicago"] == 22

def test_group_by_max(analyzer):
    result = analyzer.group_by("city", "salary", "max")
    assert result["LA"] == 95000

def test_group_by_invalid_func(analyzer):
    with pytest.raises(ValueError):
        analyzer.group_by("city", "salary", "median")


# --- Export ---

def test_to_dict_list(analyzer):
    rows = analyzer.to_dict_list()
    assert len(rows) == 7
    assert rows[0]["name"] == "Alice"

def test_export_all(analyzer):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        out_path = f.name
    try:
        analyzer.export(out_path)
        with open(out_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 7
        assert "name" in rows[0]
    finally:
        os.unlink(out_path)

def test_export_filtered(analyzer):
    filtered = analyzer.filter_rows("city", "==", "NYC")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        out_path = f.name
    try:
        analyzer.export(out_path, rows=filtered)
        with open(out_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 3
    finally:
        os.unlink(out_path)
