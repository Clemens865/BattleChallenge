# DataStore API Changelog

## v2.0.0 (2026-03-01) — BREAKING CHANGES

### Migration from v1 to v2

This is a major release with breaking changes. All clients must update.

#### URL Changes
- All endpoint paths now use `/v2/` prefix instead of `/v1/`
- Example: `/v1/items` is now `/v2/items`

#### Authentication Changes
- **REMOVED**: `X-API-Key` header authentication
- **NEW**: OAuth 2.0 Bearer token authentication
- Pass token via `Authorization: Bearer <your_token>` header
- Tokens are obtained from the `/v2/auth/token` endpoint
- The `api_key` parameter is now used as the `client_secret` in the token exchange

#### Response Format Changes
- **REMOVED**: XML response format
- **NEW**: All responses are now JSON (`application/json`)
- Request bodies must also be sent as JSON
- Set `Content-Type: application/json` and `Accept: application/json`

#### New Endpoint
- **POST /v2/search** — Full-text search across items with filters

#### Deprecation Notices
- The v1 API will be shut down on 2026-06-01
- XML support is permanently removed

## v1.5.2 (2025-12-15)
- Bug fix: rate limiting now correctly resets at midnight UTC
- Added X-RateLimit header to all responses

## v1.5.0 (2025-11-01)
- Added offset-based pagination to list endpoints
- New fields: created_at, updated_at on items
