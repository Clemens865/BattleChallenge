"""Outcome-based tests for file organizer task."""
import importlib.util
import os
import tempfile
import pytest


def load_solution():
    """Load organize_files from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "file_organizer.py")
    if not os.path.exists(module_path):
        pytest.skip(f"file_organizer.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("file_organizer", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.organize_files


@pytest.fixture
def organize():
    return load_solution()


def _create_files(directory, filenames):
    """Helper: create empty files in a directory."""
    for name in filenames:
        path = os.path.join(directory, name)
        with open(path, "w") as f:
            f.write(name)


def test_basic_organization(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["photo.jpg", "doc.pdf", "notes.txt"])
        result = organize(src, tgt)
        assert os.path.isfile(os.path.join(tgt, "jpg", "photo.jpg"))
        assert os.path.isfile(os.path.join(tgt, "pdf", "doc.pdf"))
        assert os.path.isfile(os.path.join(tgt, "txt", "notes.txt"))


def test_returns_correct_mapping(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["a.txt", "b.txt", "c.pdf"])
        result = organize(src, tgt)
        assert sorted(result.get("txt", [])) == ["a.txt", "b.txt"]
        assert result.get("pdf", []) == ["c.pdf"]


def test_files_removed_from_source(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["file.txt"])
        organize(src, tgt)
        assert not os.path.exists(os.path.join(src, "file.txt"))


def test_no_extension_goes_to_other(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["Makefile", "README"])
        result = organize(src, tgt)
        assert os.path.isfile(os.path.join(tgt, "other", "Makefile"))
        assert os.path.isfile(os.path.join(tgt, "other", "README"))


def test_extensions_are_lowercase(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["image.JPG", "doc.Pdf"])
        result = organize(src, tgt)
        assert os.path.isdir(os.path.join(tgt, "jpg"))
        assert os.path.isdir(os.path.join(tgt, "pdf"))


def test_skips_subdirectories(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        os.makedirs(os.path.join(src, "subdir"))
        _create_files(src, ["file.txt"])
        organize(src, tgt)
        assert not os.path.exists(os.path.join(tgt, "other", "subdir"))
        assert os.path.isdir(os.path.join(src, "subdir"))


def test_duplicate_name_handling(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["report.txt"])
        # Pre-create a conflicting file in target
        os.makedirs(os.path.join(tgt, "txt"), exist_ok=True)
        with open(os.path.join(tgt, "txt", "report.txt"), "w") as f:
            f.write("existing")
        organize(src, tgt)
        assert os.path.isfile(os.path.join(tgt, "txt", "report.txt"))
        assert os.path.isfile(os.path.join(tgt, "txt", "report_1.txt"))


def test_empty_source_directory(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        result = organize(src, tgt)
        assert result == {} or result == dict()


def test_source_directory_still_exists(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        _create_files(src, ["file.txt"])
        organize(src, tgt)
        assert os.path.isdir(src)


def test_file_content_preserved(organize):
    with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as tgt:
        filepath = os.path.join(src, "data.txt")
        with open(filepath, "w") as f:
            f.write("important content")
        organize(src, tgt)
        with open(os.path.join(tgt, "txt", "data.txt")) as f:
            assert f.read() == "important content"
