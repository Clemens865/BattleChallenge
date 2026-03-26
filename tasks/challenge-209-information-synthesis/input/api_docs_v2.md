# DataStore API v2 Documentation

## Base URL
```
https://api.datastore.example.com/v2
```

## Authentication
All requests require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### 1. List Items
```
GET /v2/items
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| cursor | string | Pagination cursor from previous response |
| limit | integer | Items per page (default: 20, max: 100) |

**Response 200:**
```json
{
  "data": [
    {
      "id": "item_123",
      "name": "Widget",
      "description": "A useful widget",
      "price": 29.99,
      "category": "electronics",
      "created_at": "2026-03-01T10:00:00Z",
      "updated_at": "2026-03-01T10:00:00Z"
    }
  ],
  "next_cursor": "eyJpZCI6MTIzfQ==",
  "has_more": true
}
```

### 2. Get Item
```
GET /v2/items/{item_id}
```

**Response 200:**
```json
{
  "id": "item_123",
  "name": "Widget",
  "description": "A useful widget",
  "price": 29.99,
  "category": "electronics",
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T10:00:00Z"
}
```

### 3. Create Item
```
POST /v2/items
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Widget",
  "description": "Another widget",
  "price": 19.99,
  "category": "electronics"
}
```

**Response 201:**
Returns the created item object.

### 4. Update Item
```
PUT /v2/items/{item_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Updated Widget",
  "price": 24.99
}
```

**Response 200:**
Returns the updated item object.

### 5. Delete Item
```
DELETE /v2/items/{item_id}
```

**Response 200:**
```json
{
  "deleted": true,
  "id": "item_123"
}
```

### 6. Search Items
```
POST /v2/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "widget",
  "filters": {
    "category": "electronics",
    "min_price": 10.00,
    "max_price": 50.00
  }
}
```

**Response 200:**
```json
{
  "results": [
    {
      "id": "item_123",
      "name": "Widget",
      "score": 0.95
    }
  ],
  "total": 1
}
```

## Error Responses

All errors return JSON:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Item not found"
  }
}
```

**Status Codes:**
- 400 — Bad request
- 401 — Unauthorized (invalid/missing token)
- 404 — Resource not found
- 429 — Rate limited
- 500 — Internal server error
