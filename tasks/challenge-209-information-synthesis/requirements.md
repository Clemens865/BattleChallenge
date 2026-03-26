# Challenge 209: Multi-Source Information Synthesis

## Objective

Fix a broken Python API client by gathering information from 4 different sources. The client broke because the external API migrated from v1 to v2.

## Input

Four information sources in `input/`:

1. **`input/client_code/api_client.py`** — The broken Python API client (uses v1 patterns)
2. **`input/changelog.md`** — Release notes mentioning the v1-to-v2 migration
3. **`input/api_docs_v2.md`** — The new v2 API documentation with all 6 endpoints
4. **`input/slack_thread.txt`** — A team Slack conversation with additional migration details

Each source contains unique information needed for a complete fix:
- The client code shows what needs to change
- The changelog explains auth and format changes
- The API docs define the new endpoints
- The Slack thread reveals pagination and rate limit changes

## Requirements

Fix the API client to work with the v2 API. Use **ALL** available information sources. The fixed client must handle:

1. **v2 URL paths** — All endpoints use `/v2/` prefix
2. **Bearer token auth** — Changed from API key header to Bearer token
3. **JSON responses** — Changed from XML to JSON
4. **All 6 endpoints** — list, get, create, update, delete, search
5. **Cursor-based pagination** — Changed from offset-based
6. **Updated rate limit headers** — `X-Rate-Limit-Remaining` instead of `X-RateLimit`
7. **Proper error handling** — Non-200 responses raise exceptions

## Required Output

Place the fixed `api_client.py` in the output directory.

## Scoring

**Binary**: ALL verification tests must pass or score is 0. A framework that only reads the client code will miss changes documented in other sources.
