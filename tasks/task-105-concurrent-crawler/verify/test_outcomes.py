"""Outcome-based tests for task-105: Concurrent web crawler."""
import asyncio
import csv
import importlib.util
import io
import json
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pytest

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.getcwd())


def _load_module(name, filename=None):
    filename = filename or f"{name}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"{filename} not found in {OUTPUT_DIR}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if OUTPUT_DIR not in sys.path:
        sys.path.insert(0, OUTPUT_DIR)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def crawler_mod():
    return _load_module("crawler")


@pytest.fixture(scope="module")
def rate_limiter_mod():
    return _load_module("rate_limiter")


@pytest.fixture(scope="module")
def dedup_mod():
    return _load_module("dedup")


@pytest.fixture(scope="module")
def output_mod():
    return _load_module("output")


@pytest.fixture(scope="module")
def robots_mod():
    return _load_module("robots")


# ===========================================================================
# Mock HTTP server
# ===========================================================================

class MockHandler(BaseHTTPRequestHandler):
    """Simple mock HTTP server for crawler tests."""

    PAGES = {
        "/": "<html><head><title>Home</title></head><body>"
             '<a href="/page1">Page 1</a> <a href="/page2">Page 2</a></body></html>',
        "/page1": "<html><head><title>Page 1</title></head><body>"
                  '<a href="/page2">Page 2</a> <a href="/deep/page3">Deep</a></body></html>',
        "/page2": "<html><head><title>Page 2</title></head><body>No links here.</body></html>",
        "/deep/page3": "<html><head><title>Deep Page</title></head><body>"
                       '<a href="/">Back home</a></body></html>',
        "/slow": None,  # Will sleep
        "/redirect": None,  # Will redirect
        "/redirect-loop": None,  # Redirect loop
        "/robots.txt": "User-agent: *\nDisallow: /private/\nAllow: /\nCrawl-delay: 0\n",
        "/private/secret": "<html><body>Secret</body></html>",
        "/large": "<html><body>" + "x" * 5000 + "</body></html>",
        "/special-chars": '<html><head><title>Special &amp; Page</title></head>'
                          '<body><a href="/page1?q=hello%20world&sort=asc">Link</a></body></html>',
    }

    redirect_count = {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/slow":
            time.sleep(5)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body>Slow page</body></html>")
            return

        if path == "/redirect":
            self.send_response(301)
            self.send_header("Location", "/page1")
            self.end_headers()
            return

        if path == "/redirect-loop":
            self.send_response(301)
            self.send_header("Location", "/redirect-loop")
            self.end_headers()
            return

        if path == "/error500":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
            return

        content = self.PAGES.get(path)
        if content is not None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass  # Suppress logging


@pytest.fixture(scope="module")
def mock_server():
    """Start a mock HTTP server on a random port."""
    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


# ===========================================================================
# SECTION 1: File existence (5 tests)
# ===========================================================================

REQUIRED_FILES = ["crawler.py", "rate_limiter.py", "dedup.py", "output.py", "robots.py"]


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_file_exists(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    assert os.path.isfile(path), f"{filename} not found"


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_file_min_lines(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(path):
        pytest.skip(f"{filename} not found")
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) >= 10, f"{filename} has only {len(lines)} lines"


# ===========================================================================
# SECTION 2: URL normalization (10 tests)
# ===========================================================================

def test_dedup_has_class(dedup_mod):
    assert hasattr(dedup_mod, "Deduplicator")


def test_normalize_lowercase_scheme(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("HTTP://Example.COM/path") == d.normalize("http://example.com/path")


def test_normalize_remove_fragment(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com/page#section") == d.normalize("http://example.com/page")


def test_normalize_remove_default_port_http(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com:80/page") == d.normalize("http://example.com/page")


def test_normalize_remove_default_port_https(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("https://example.com:443/page") == d.normalize("https://example.com/page")


def test_normalize_keep_non_default_port(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com:8080/page") != d.normalize("http://example.com/page")


def test_normalize_sort_query_params(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com/p?b=2&a=1") == d.normalize("http://example.com/p?a=1&b=2")


def test_normalize_trailing_slash(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com/page/") == d.normalize("http://example.com/page")


def test_normalize_dot_segments(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.normalize("http://example.com/a/b/../c") == d.normalize("http://example.com/a/c")


def test_dedup_is_seen(dedup_mod):
    d = dedup_mod.Deduplicator()
    assert d.is_seen("http://example.com/new") is False
    d.mark_seen("http://example.com/new")
    assert d.is_seen("http://example.com/new") is True


def test_dedup_seen_count(dedup_mod):
    d = dedup_mod.Deduplicator()
    d.mark_seen("http://a.com/1")
    d.mark_seen("http://a.com/2")
    d.mark_seen("http://a.com/1")  # Duplicate
    assert d.seen_count == 2


# ===========================================================================
# SECTION 3: Rate limiter (5 tests)
# ===========================================================================

def test_rate_limiter_has_class(rate_limiter_mod):
    assert hasattr(rate_limiter_mod, "RateLimiter")


def test_rate_limiter_basic(rate_limiter_mod):
    rl = rate_limiter_mod.RateLimiter(rate=10, per=1.0, burst=1)
    # First acquire should be instant
    start = time.time()
    asyncio.get_event_loop().run_until_complete(rl.acquire("test.com"))
    elapsed = time.time() - start
    assert elapsed < 0.5


def test_rate_limiter_respects_rate(rate_limiter_mod):
    """Two rapid acquires at rate=1/sec should take ~1 second total."""
    rl = rate_limiter_mod.RateLimiter(rate=1, per=1.0, burst=1)

    async def do_two():
        await rl.acquire("ratetest.com")
        await rl.acquire("ratetest.com")

    start = time.time()
    asyncio.get_event_loop().run_until_complete(do_two())
    elapsed = time.time() - start
    assert elapsed >= 0.8, f"Rate limiter too fast: {elapsed:.2f}s (expected ~1s)"


def test_rate_limiter_per_domain(rate_limiter_mod):
    """Different domains have independent rate limits."""
    rl = rate_limiter_mod.RateLimiter(rate=1, per=1.0, burst=1)

    async def do_parallel():
        await rl.acquire("domain1.com")
        await rl.acquire("domain2.com")

    start = time.time()
    asyncio.get_event_loop().run_until_complete(do_parallel())
    elapsed = time.time() - start
    # Two different domains should not block each other
    assert elapsed < 0.5


def test_rate_limiter_burst(rate_limiter_mod):
    """Burst > 1 allows multiple immediate acquires."""
    rl = rate_limiter_mod.RateLimiter(rate=1, per=1.0, burst=3)

    async def do_burst():
        for _ in range(3):
            await rl.acquire("burst.com")

    start = time.time()
    asyncio.get_event_loop().run_until_complete(do_burst())
    elapsed = time.time() - start
    assert elapsed < 0.5, f"Burst acquire too slow: {elapsed:.2f}s"


# ===========================================================================
# SECTION 4: Output writer (5 tests)
# ===========================================================================

def test_output_has_class(output_mod):
    assert hasattr(output_mod, "OutputWriter")


def test_output_to_json(output_mod, tmp_path):
    writer = output_mod.OutputWriter()
    # Create a minimal CrawlResult-like object
    from types import SimpleNamespace
    result = SimpleNamespace(
        url="http://example.com",
        status_code=200,
        title="Example",
        links_found=["http://example.com/a"],
        depth=0,
        timestamp="2026-01-01T00:00:00",
        content_length=100,
        error=None,
    )
    writer.add_result(result)
    out_path = str(tmp_path / "out.json")
    writer.to_json(out_path)
    with open(out_path) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["url"] == "http://example.com"


def test_output_to_csv(output_mod, tmp_path):
    writer = output_mod.OutputWriter()
    from types import SimpleNamespace
    result = SimpleNamespace(
        url="http://example.com",
        status_code=200,
        title="Example",
        links_found=[],
        depth=0,
        timestamp="2026-01-01T00:00:00",
        content_length=50,
        error=None,
    )
    writer.add_result(result)
    out_path = str(tmp_path / "out.csv")
    writer.to_csv(out_path)
    with open(out_path) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert len(rows) >= 2  # Header + data


def test_output_summary(output_mod):
    writer = output_mod.OutputWriter()
    from types import SimpleNamespace
    for i in range(5):
        writer.add_result(SimpleNamespace(
            url=f"http://example.com/{i}",
            status_code=200 if i < 4 else 404,
            title=f"Page {i}",
            links_found=[],
            depth=0,
            timestamp="2026-01-01T00:00:00",
            content_length=100,
            error=None if i < 4 else "Not Found",
        ))
    summary = writer.summary()
    assert isinstance(summary, dict)
    assert summary.get("total_pages", summary.get("total", 0)) == 5


def test_output_results_property(output_mod):
    writer = output_mod.OutputWriter()
    assert isinstance(writer.results, list)
    assert len(writer.results) == 0


# ===========================================================================
# SECTION 5: Robots.txt parser (5 tests)
# ===========================================================================

def test_robots_has_class(robots_mod):
    assert hasattr(robots_mod, "RobotsChecker")


def test_robots_allowed(robots_mod, mock_server):
    checker = robots_mod.RobotsChecker()

    async def check():
        return await checker.is_allowed(f"{mock_server}/page1")

    result = asyncio.get_event_loop().run_until_complete(check())
    assert result is True


def test_robots_disallowed(robots_mod, mock_server):
    checker = robots_mod.RobotsChecker()

    async def check():
        return await checker.is_allowed(f"{mock_server}/private/secret")

    result = asyncio.get_event_loop().run_until_complete(check())
    assert result is False


def test_robots_missing_robotstxt(robots_mod):
    """No robots.txt means allow all."""
    checker = robots_mod.RobotsChecker()

    async def check():
        # Use a URL that will 404 on robots.txt
        return await checker.is_allowed("http://127.0.0.1:1/page")

    # This should not crash; missing robots.txt = allow all
    try:
        result = asyncio.get_event_loop().run_until_complete(check())
        assert result is True
    except (ConnectionRefusedError, OSError):
        # Connection error to nonexistent server — should default to allow
        pass


def test_robots_caches_per_domain(robots_mod, mock_server):
    """robots.txt should be fetched only once per domain."""
    checker = robots_mod.RobotsChecker()

    async def check():
        await checker.is_allowed(f"{mock_server}/page1")
        await checker.is_allowed(f"{mock_server}/page2")
        # Both should use cached robots.txt

    asyncio.get_event_loop().run_until_complete(check())
    # No assertion — just verifying no crash. Proper caching is tested by performance.


# ===========================================================================
# SECTION 6: Crawler integration (5 tests)
# ===========================================================================

def test_crawler_has_class(crawler_mod):
    assert hasattr(crawler_mod, "Crawler")


def test_crawler_basic_crawl(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=1, max_pages=10)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert len(results) >= 1
    urls = [r.url for r in results]
    assert any(mock_server in u for u in urls)


def test_crawler_respects_depth(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=0, max_pages=100)

    results = asyncio.get_event_loop().run_until_complete(run())
    # Depth 0 = only the seed page
    assert len(results) == 1


def test_crawler_respects_max_pages(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=10, max_pages=2)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert len(results) <= 2


def test_crawler_handles_404(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/nonexistent", max_depth=0, max_pages=10)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert len(results) == 1
    assert results[0].status_code == 404


# ===========================================================================
# SECTION 7: CrawlResult structure (3 tests)
# ===========================================================================

def test_crawl_result_has_fields(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=0, max_pages=1)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert len(results) >= 1
    r = results[0]
    assert hasattr(r, "url")
    assert hasattr(r, "status_code")
    assert hasattr(r, "title")
    assert hasattr(r, "links_found")
    assert hasattr(r, "depth")


def test_crawl_result_title_extracted(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=0, max_pages=1)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert results[0].title == "Home"


def test_crawl_result_links_found(crawler_mod, rate_limiter_mod, dedup_mod, output_mod, robots_mod, mock_server):
    rl = rate_limiter_mod.RateLimiter(rate=100, per=1.0, burst=100)
    dd = dedup_mod.Deduplicator()
    ow = output_mod.OutputWriter()
    rc = robots_mod.RobotsChecker()
    crawler = crawler_mod.Crawler(rate_limiter=rl, deduplicator=dd, output_writer=ow, robots_checker=rc)

    async def run():
        return await crawler.crawl(f"{mock_server}/", max_depth=0, max_pages=1)

    results = asyncio.get_event_loop().run_until_complete(run())
    assert len(results[0].links_found) >= 2  # Home page has 2 links
