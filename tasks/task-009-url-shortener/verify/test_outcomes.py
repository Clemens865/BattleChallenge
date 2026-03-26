"""Outcome-based tests for URL shortener task."""
import importlib.util
import os
import tempfile
import pytest


def load_solution():
    """Load URLShortener from the output directory."""
    output_dir = os.environ.get("OUTPUT_DIR", os.getcwd())
    module_path = os.path.join(output_dir, "url_shortener.py")
    if not os.path.exists(module_path):
        pytest.skip(f"url_shortener.py not found in {output_dir}")
    spec = importlib.util.spec_from_file_location("url_shortener", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.URLShortener


@pytest.fixture
def URLShortener():
    return load_solution()


@pytest.fixture
def shortener(URLShortener):
    return URLShortener()


# --- Shorten ---

def test_shorten_returns_short_url(shortener):
    result = shortener.shorten("https://example.com/very/long/path")
    assert result.startswith("https://short.url/")

def test_short_code_length(shortener):
    result = shortener.shorten("https://example.com")
    code = result.split("/")[-1]
    assert 6 <= len(code) <= 8

def test_short_code_is_alphanumeric(shortener):
    result = shortener.shorten("https://example.com")
    code = result.split("/")[-1]
    assert code.isalnum()

def test_same_url_same_code(shortener):
    r1 = shortener.shorten("https://example.com/page")
    r2 = shortener.shorten("https://example.com/page")
    assert r1 == r2

def test_different_urls_different_codes(shortener):
    r1 = shortener.shorten("https://example.com/a")
    r2 = shortener.shorten("https://example.com/b")
    assert r1 != r2

def test_invalid_url_raises(shortener):
    with pytest.raises(ValueError):
        shortener.shorten("not-a-url")

def test_ftp_url_raises(shortener):
    with pytest.raises(ValueError):
        shortener.shorten("ftp://example.com")

def test_custom_base_url(URLShortener):
    s = URLShortener(base_url="https://my.co")
    result = s.shorten("https://example.com")
    assert result.startswith("https://my.co/")


# --- Resolve ---

def test_resolve_full_url(shortener):
    short = shortener.shorten("https://example.com/test")
    resolved = shortener.resolve(short)
    assert resolved == "https://example.com/test"

def test_resolve_code_only(shortener):
    short = shortener.shorten("https://example.com/test")
    code = short.split("/")[-1]
    resolved = shortener.resolve(code)
    assert resolved == "https://example.com/test"

def test_resolve_unknown_raises(shortener):
    with pytest.raises(KeyError):
        shortener.resolve("https://short.url/nonexistent")


# --- Stats ---

def test_stats_basic(shortener):
    short = shortener.shorten("https://example.com")
    stats = shortener.get_stats(short)
    assert stats["long_url"] == "https://example.com"
    assert stats["access_count"] == 0
    assert "created_at" in stats

def test_stats_access_count_increments(shortener):
    short = shortener.shorten("https://example.com")
    shortener.resolve(short)
    shortener.resolve(short)
    stats = shortener.get_stats(short)
    assert stats["access_count"] == 2


# --- List ---

def test_list_empty(shortener):
    assert shortener.list_urls() == []

def test_list_after_adding(shortener):
    shortener.shorten("https://a.com")
    shortener.shorten("https://b.com")
    urls = shortener.list_urls()
    assert len(urls) == 2
    long_urls = {u["long_url"] for u in urls}
    assert "https://a.com" in long_urls
    assert "https://b.com" in long_urls


# --- Delete ---

def test_delete_removes_url(shortener):
    short = shortener.shorten("https://example.com")
    shortener.delete(short)
    with pytest.raises(KeyError):
        shortener.resolve(short)

def test_delete_unknown_raises(shortener):
    with pytest.raises(KeyError):
        shortener.delete("https://short.url/nonexistent")


# --- Persistence ---

def test_persistence(URLShortener):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        s1 = URLShortener(storage_path=path)
        short = s1.shorten("https://example.com/persistent")
        s2 = URLShortener(storage_path=path)
        resolved = s2.resolve(short)
        assert resolved == "https://example.com/persistent"
    finally:
        if os.path.exists(path):
            os.unlink(path)
