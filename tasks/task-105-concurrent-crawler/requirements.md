# Task 105: Concurrent Web Crawler

## Objective

Build a concurrent web crawler with rate limiting, URL deduplication, robots.txt compliance, and structured output.

## Required Output Files

### 1. `crawler.py`
Main crawler module providing:
- `Crawler` class with `async crawl(seed_url, max_depth=3, max_pages=100)` method
- Uses `asyncio` and `aiohttp` (or `urllib` with async wrappers) for concurrent fetching
- Accepts a `RateLimiter`, `Deduplicator`, `RobotsChecker`, and `OutputWriter` as dependencies
- Returns a list of `CrawlResult` objects

`CrawlResult` fields: `url`, `status_code`, `title`, `links_found` (list of URLs), `depth`, `timestamp`, `content_length`, `error` (None or error string)

### 2. `rate_limiter.py`
Token bucket rate limiter:
- `RateLimiter` class with `__init__(self, rate: float, per: float = 1.0, burst: int = 1)`
- `async acquire(domain: str)` — blocks until a token is available for the given domain
- Per-domain rate limiting (each domain has its own bucket)
- `burst` parameter controls max tokens that can accumulate
- Must be accurate to within 100ms

### 3. `dedup.py`
URL deduplication module:
- `Deduplicator` class
- `normalize(url: str) -> str` — normalize a URL (lowercase scheme/host, remove fragments, remove default ports, sort query params, remove trailing slash on paths, resolve `..` and `.` in paths)
- `is_seen(url: str) -> bool` — returns True if normalized URL was already seen
- `mark_seen(url: str)` — mark a URL as seen
- `seen_count` property — number of unique URLs seen

### 4. `output.py`
Structured output module:
- `OutputWriter` class
- `add_result(result: CrawlResult)` — accumulate results
- `to_json(path: str)` — write results as JSON array
- `to_csv(path: str)` — write results as CSV
- `results` property — list of all results
- `summary()` — returns dict with stats: total pages, success count, error count, avg response time, domains crawled

### 5. `robots.py`
robots.txt parser and enforcer:
- `RobotsChecker` class
- `async is_allowed(url: str, user_agent: str = "*") -> bool` — check if URL is crawlable
- Caches robots.txt per domain (fetches only once per domain)
- Handles missing robots.txt (allow all)
- Handles malformed robots.txt (allow all)
- Respects `Disallow` and `Allow` directives
- Respects `Crawl-delay` directive (feeds into rate limiter)

## Constraints

- Must use Python's `asyncio` for concurrency
- May use `aiohttp` as the only external dependency (tests provide a mock server, so actual HTTP library is abstracted)
- Must handle errors gracefully: timeouts, connection errors, HTTP errors, malformed HTML, redirect loops
- Maximum redirect chain: 10 (then treat as error)
- User-Agent header must be configurable
- Each file must be at least 10 lines
- No global mutable state — all state lives in class instances

## Scoring

**Binary**: ALL tests must pass or score is 0. Tests use a mock HTTP server (started as a pytest fixture) and verify:
- Rate limiting accuracy (requests properly spaced)
- URL normalization (20+ edge cases)
- Deduplication correctness
- robots.txt compliance
- Depth limiting
- Error handling (404, 500, timeout, redirect loops)
- Output format (valid JSON and CSV)
- Concurrent performance (N pages in under M seconds)
- Correct link extraction from HTML
