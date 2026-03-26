"""Outcome-based tests for data pipeline task."""
import importlib.util
import os
import pytest


def load_solution():
    """Load pipeline module from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "pipeline.py")
    if not os.path.exists(module_path):
        pytest.skip(f"pipeline.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("pipeline", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return load_solution()


@pytest.fixture
def Pipeline(mod):
    return mod.Pipeline


@pytest.fixture
def sample_data():
    return [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 17, "city": "LA"},
        {"name": "Charlie", "age": 25, "city": "NYC"},
        {"name": "Diana", "age": 16, "city": "Chicago"},
        {"name": "Eve", "age": 35, "city": "NYC"},
    ]


# --- Pipeline basics ---

def test_empty_pipeline(Pipeline, sample_data):
    p = Pipeline()
    result = p.run(sample_data)
    assert result == sample_data

def test_single_step(Pipeline, mod, sample_data):
    p = Pipeline()
    p.add_step("filter_adults", mod.filter_rows("age", lambda x: x >= 18))
    result = p.run(sample_data)
    assert len(result) == 3
    assert all(r["age"] >= 18 for r in result)

def test_chaining(Pipeline, mod, sample_data):
    p = Pipeline()
    result = (
        p.add_step("filter", mod.filter_rows("age", lambda x: x >= 18))
         .add_step("sort", mod.sort_by("age"))
         .run(sample_data)
    )
    ages = [r["age"] for r in result]
    assert ages == sorted(ages)
    assert len(result) == 3


# --- Transform functions ---

def test_filter_rows(mod):
    data = [{"x": 1}, {"x": 2}, {"x": 3}]
    fn = mod.filter_rows("x", lambda v: v > 1)
    assert fn(data) == [{"x": 2}, {"x": 3}]

def test_map_column(mod):
    data = [{"name": "alice"}, {"name": "bob"}]
    fn = mod.map_column("name", str.upper)
    result = fn(data)
    assert result[0]["name"] == "ALICE"
    assert result[1]["name"] == "BOB"

def test_add_column(mod):
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    fn = mod.add_column("sum", lambda row: row["a"] + row["b"])
    result = fn(data)
    assert result[0]["sum"] == 3
    assert result[1]["sum"] == 7

def test_sort_by_ascending(mod):
    data = [{"v": 3}, {"v": 1}, {"v": 2}]
    fn = mod.sort_by("v")
    result = fn(data)
    assert [r["v"] for r in result] == [1, 2, 3]

def test_sort_by_descending(mod):
    data = [{"v": 3}, {"v": 1}, {"v": 2}]
    fn = mod.sort_by("v", reverse=True)
    result = fn(data)
    assert [r["v"] for r in result] == [3, 2, 1]

def test_deduplicate(mod):
    data = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}, {"id": 1, "v": "c"}]
    fn = mod.deduplicate("id")
    result = fn(data)
    assert len(result) == 2
    ids = [r["id"] for r in result]
    assert 1 in ids and 2 in ids


# --- Multi-step pipeline ---

def test_multi_step_pipeline(Pipeline, mod, sample_data):
    p = Pipeline()
    p.add_step("filter", mod.filter_rows("age", lambda x: x >= 18))
    p.add_step("upper_name", mod.map_column("name", str.upper))
    p.add_step("sort", mod.sort_by("age", reverse=True))
    result = p.run(sample_data)
    assert len(result) == 3
    assert result[0]["name"] == "EVE"
    assert result[0]["age"] == 35
    assert result[-1]["name"] == "CHARLIE"

def test_pipeline_with_add_column(Pipeline, mod, sample_data):
    p = Pipeline()
    p.add_step("label", mod.add_column("label", lambda r: f"{r['name']}-{r['age']}"))
    result = p.run(sample_data)
    assert result[0]["label"] == "Alice-30"
    assert result[1]["label"] == "Bob-17"


# --- Trace ---

def test_run_with_trace(Pipeline, mod, sample_data):
    p = Pipeline()
    p.add_step("filter", mod.filter_rows("age", lambda x: x >= 18))
    p.add_step("sort", mod.sort_by("name"))
    trace = p.run_with_trace(sample_data)
    assert "result" in trace
    assert "steps" in trace
    assert "total_duration_ms" in trace
    assert len(trace["steps"]) == 2
    assert trace["steps"][0]["name"] == "filter"
    assert trace["steps"][0]["input_count"] == 5
    assert trace["steps"][0]["output_count"] == 3
    assert trace["steps"][1]["name"] == "sort"
    assert trace["steps"][1]["input_count"] == 3
    assert trace["steps"][1]["output_count"] == 3
    assert len(trace["result"]) == 3


# --- Remove step ---

def test_remove_step(Pipeline, mod, sample_data):
    p = Pipeline()
    p.add_step("filter", mod.filter_rows("age", lambda x: x >= 18))
    p.add_step("sort", mod.sort_by("age"))
    p.remove_step("filter")
    result = p.run(sample_data)
    assert len(result) == 5  # filter was removed, all rows remain

def test_remove_nonexistent_raises(Pipeline):
    p = Pipeline()
    with pytest.raises(ValueError):
        p.remove_step("nope")


# --- Edge cases ---

def test_empty_data(Pipeline, mod):
    p = Pipeline()
    p.add_step("filter", mod.filter_rows("x", lambda v: v > 0))
    assert p.run([]) == []

def test_does_not_mutate_input(Pipeline, mod, sample_data):
    original = [dict(row) for row in sample_data]
    p = Pipeline()
    p.add_step("filter", mod.filter_rows("age", lambda x: x >= 18))
    p.run(sample_data)
    assert sample_data == original
