# Product Requirements Document: Inventory Management API

## Overview

Build a RESTful inventory management API using Python. The API manages items, categories, and users with JWT-based authentication. All data is stored in a SQLite database.

## Database Schema

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL |
| role | TEXT | DEFAULT 'user' |
| created_at | TEXT | ISO 8601 timestamp |

### Categories Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE, NOT NULL |
| description | TEXT | |

### Items Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| description | TEXT | |
| price | REAL | NOT NULL, >= 0 |
| quantity | INTEGER | NOT NULL, DEFAULT 0 |
| category_id | INTEGER | FOREIGN KEY -> categories(id) |
| created_at | TEXT | ISO 8601 timestamp |
| updated_at | TEXT | ISO 8601 timestamp |

## Authentication

- Users authenticate via POST /auth/login with `{"username": "...", "password": "..."}`
- Server returns `{"token": "<jwt_token>", "expires_in": 3600}`
- JWT payload includes: `{"user_id": <id>, "username": "<name>", "role": "<role>"}`
- All API endpoints (except /auth/login) require `Authorization: Bearer <token>` header
- Invalid/missing tokens return 401 with `{"error": "Unauthorized", "status": 401}`
- JWT secret key: configurable, default `"inventory-secret-key-2026"`

## API Endpoints

### 1. GET /items
List all items with pagination.

**Query Parameters:**
- `page` (integer, default: 1) — page number
- `limit` (integer, default: 20, max: 100) — items per page

**Response 200:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Widget",
      "description": "A useful widget",
      "price": 9.99,
      "quantity": 100,
      "category_id": 1,
      "created_at": "2026-03-26T10:00:00Z",
      "updated_at": "2026-03-26T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

### 2. POST /items
Create a new item.

**Request body:**
```json
{
  "name": "Widget",
  "description": "A useful widget",
  "price": 9.99,
  "quantity": 100,
  "category_id": 1
}
```

**Validation:**
- `name` is required, non-empty string
- `price` is required, must be >= 0
- `quantity` must be >= 0 if provided
- `category_id` must reference an existing category

**Response 201:**
```json
{
  "id": 1,
  "name": "Widget",
  "description": "A useful widget",
  "price": 9.99,
  "quantity": 100,
  "category_id": 1,
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z"
}
```

**Response 422 (validation error):**
```json
{
  "error": "Validation failed",
  "status": 422,
  "details": [
    {"field": "name", "message": "Name is required"},
    {"field": "price", "message": "Price must be >= 0"}
  ]
}
```

### 3. GET /items/:id
Get a single item by ID.

**Response 200:** Single item object (same shape as items in list)

**Response 404:**
```json
{"error": "Item not found", "status": 404}
```

### 4. PUT /items/:id
Update an existing item.

**Request body:** Same as POST (all fields optional for update)

**Response 200:** Updated item object

**Response 404:** Same as GET

**Response 422:** Same validation as POST

### 5. DELETE /items/:id
Delete an item.

**Response 200:**
```json
{"message": "Item deleted", "id": 1}
```

**Response 404:** Same as GET

### 6. GET /categories
List all categories.

**Response 200:**
```json
{
  "categories": [
    {"id": 1, "name": "Electronics", "description": "Electronic devices and components"}
  ]
}
```

### 7. POST /search
Search items with filters.

**Request body:**
```json
{
  "name": "widget",
  "category": "Electronics",
  "min_price": 5.00,
  "max_price": 50.00
}
```

All fields are optional. `name` does a case-insensitive partial match. `category` matches by category name.

**Response 200:**
```json
{
  "results": [...],
  "count": 5
}
```

## Seed Data

The database should be pre-populated with:

**Categories:**
1. Electronics — "Electronic devices and components"
2. Books — "Physical and digital books"
3. Clothing — "Apparel and accessories"

**Users:**
1. admin / admin123 (role: admin)
2. user1 / password1 (role: user)

**Items:** (at least 5)
1. Wireless Mouse — Electronics, $29.99, qty 150
2. USB-C Cable — Electronics, $12.99, qty 300
3. Python Handbook — Books, $45.00, qty 50
4. Cotton T-Shirt — Clothing, $19.99, qty 200
5. Mechanical Keyboard — Electronics, $89.99, qty 75

## Error Format

All error responses MUST use this consistent format:
```json
{"error": "<human readable message>", "status": <http_status_code>}
```

Validation errors add a `details` array with per-field messages.
