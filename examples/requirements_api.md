# REST API: User Management

## Base URL
`https://api.example.com/v1`

## Endpoints

### POST /users - Create User
**Request Body:**
```json
{
  "name": "string (2-50 chars, required)",
  "email": "string (valid email, required, unique)",
  "password": "string (8-128 chars, must contain uppercase, lowercase, digit, special char)",
  "role": "string (enum: 'admin', 'user', 'viewer', default: 'user')"
}
```

**Success Response: 201 Created**
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "role": "string",
  "created_at": "ISO 8601"
}
```

**Error Responses:**
- 400: Invalid input (validation error details in body)
- 409: Email already exists
- 422: Unprocessable entity

### GET /users/:id - Get User
- Returns user by ID
- 404 if user not found
- Requires authentication (Bearer token)

### PUT /users/:id - Update User
- Partial update (only provided fields are updated)
- Cannot change email to an existing email
- Cannot change own role from admin
- Requires authentication + authorization (admin or self)

### DELETE /users/:id - Delete User
- Soft delete (sets deleted_at timestamp)
- Cannot delete own account
- Requires admin role
- 404 if user not found

### GET /users - List Users
- Query params: page (default 1), limit (default 20, max 100), role, search
- Returns paginated results with total count
- Requires admin role

## Authentication
- Bearer token in Authorization header
- Tokens expire after 1 hour
- Refresh token endpoint: POST /auth/refresh

## Rate Limiting
- 100 requests per minute per API key
- Returns 429 Too Many Requests with Retry-After header
