# Scam Shield — Frontend API Integration Guide

This guide details how the frontend client interacts with the Scam Shield FastAPI backend.

---

## Base URL & Configuration

| Environment | Base URL |
|---|---|
| Local Development | `http://localhost:8000/api/v1` |
| Interactive Swagger Docs | `http://localhost:8000/docs` |
| OpenAPI JSON Schema | `http://localhost:8000/openapi.json` |

---

## Authentication Flow

Authentication uses JWT access tokens issued via Supabase Auth.
Every protected request must pass the bearer token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

### TypeScript API Client Example (Axios)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach JWT token to all outgoing requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-handle 401 token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', res.data.access_token);
          if (res.data.refresh_token) {
            localStorage.setItem('refresh_token', res.data.refresh_token);
          }
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return axios(error.config);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## API Endpoints Reference

### 1. Authentication

#### Register
- **URL**: `POST /auth/register`
- **Auth**: None
- **Request Body**:
```json
{
  "full_name": "Jane Doe",
  "email": "jane.doe@company.com",
  "password": "Password123!",
  "department": "Engineering"
}
```
- **Response (201 Created)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4...",
  "user": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "jane.doe@company.com",
    "full_name": "Jane Doe",
    "role": "user",
    "department": "Engineering"
  }
}
```
- **Error Codes**:
  - `400 Bad Request`: Password too weak (must be >= 8 chars, 1 uppercase, 1 lowercase, 1 number).
  - `409 Conflict`: Email already registered.
  - `422 Unprocessable Entity`: Invalid email format or missing fields.

#### Login
- **URL**: `POST /auth/login`
- **Auth**: None
- **Request Body**:
```json
{
  "email": "jane.doe@company.com",
  "password": "Password123!"
}
```
- **Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4...",
  "user": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "jane.doe@company.com",
    "full_name": "Jane Doe",
    "role": "user",
    "department": "Engineering"
  }
}
```
- **Error Codes**:
  - `401 Unauthorized`: Invalid email or password.

#### Current User Profile
- **URL**: `GET /auth/me`
- **Auth**: Bearer Token
- **Response (200 OK)**:
```json
{
  "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "email": "jane.doe@company.com",
  "full_name": "Jane Doe",
  "role": "user",
  "department": "Engineering"
}
```

#### Logout
- **URL**: `POST /auth/logout`
- **Auth**: Bearer Token
- **Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

---

### 2. Simulations

#### Fetch Simulation Feed
- **URL**: `GET /simulations/`
- **Auth**: Bearer Token
- **Query Parameters**:
  - `exclude` *(string, optional)*: Comma-separated simulation UUIDs to omit (e.g. `?exclude=uuid1,uuid2`).
  - `difficulty` *(string, optional)*: `easy`, `medium`, or `hard`.
  - `attack_type` *(string, optional)*: `email`, `sms`, `social_media`, `website`, or `phone`.
  - `page` *(int, default: 1)*: Page number.
  - `page_size` *(int, default: 10, max: 50)*: Items per page.
- **Example Request**:
```http
GET /simulations/?difficulty=easy&exclude=a123e456-789b-12d3-a456-426614174000&page=1&page_size=10
```
- **Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "7b8f6c3a-2e4d-491a-b678-9e1234567890",
      "title": "Urgent Account Suspension Notice",
      "description": "An email threatening immediate account suspension unless verified.",
      "sender": "security-alert@paypa1-support.com",
      "content": "Dear Customer, Your PayPal account will be suspended in 24 hours...",
      "difficulty": "easy",
      "attack_type": "email",
      "created_at": "2026-01-15T08:30:00Z"
    }
  ],
  "total": 19,
  "page": 1,
  "page_size": 10
}
```
> **Security Note**: The field `is_phishing` is never sent in this response.

---

### 3. Simulation Responses

#### Submit User Action
- **URL**: `POST /responses/`
- **Auth**: Bearer Token
- **Request Body**:
```json
{
  "simulation_id": "7b8f6c3a-2e4d-491a-b678-9e1234567890",
  "action": "reported",
  "time_taken": 18
}
```
*Allowed actions*: `"reported"`, `"clicked"`, `"ignored"`
*`time_taken`*: integer in seconds (>= 0).
- **Response (201 Created)**:
```json
{
  "success": true,
  "is_correct": true,
  "action": "reported"
}
```
- **Error Codes**:
  - `400 Bad Request`: Invalid action or time value.
  - `404 Not Found`: Simulation ID does not exist.
  - `409 Conflict`: The user has already submitted a response for this simulation.

#### User Response History
- **URL**: `GET /responses/history`
- **Auth**: Bearer Token
- **Query Parameters**: `page` (default: 1), `page_size` (default: 10).
- **Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "d4e5f6a7-b8c9-0123-4567-89abcdef0123",
      "simulation_id": "7b8f6c3a-2e4d-491a-b678-9e1234567890",
      "action": "reported",
      "is_correct": true,
      "time_taken": 18,
      "created_at": "2026-01-15T08:32:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

### 4. User Performance (Individual)

#### Get My Performance Profile
- **URL**: `GET /users/me/performance`
- **Auth**: Bearer Token
- **Response (200 OK)**:
```json
{
  "completed_simulations": 12,
  "correct_responses": 10,
  "incorrect_responses": 2,
  "accuracy_percentage": 83.33,
  "average_response_time": 14.5,
  "risk_score": 16.67,
  "risk_level": "low"
}
```
*When user has fewer than 3 completed simulations, `risk_score` is `null` and `risk_level` is `"unassessed"`.*

---

### 5. Admin Analytics & Directory (Admin Only)

#### Full Analytics & Charts
- **URL**: `GET /analytics/`
- **Auth**: Admin Bearer Token
- **Response (200 OK)**:
```json
{
  "total_users": 150,
  "total_simulations": 20,
  "total_responses": 850,
  "correct_responses": 680,
  "incorrect_responses": 170,
  "accuracy_percentage": 80.0,
  "difficulty_data": [
    { "name": "Easy", "total": 400, "correct": 360 },
    { "name": "Medium", "total": 300, "correct": 230 },
    { "name": "Hard", "total": 150, "correct": 90 }
  ],
  "type_data": [
    { "name": "Email", "total": 500, "clicks": 60 },
    { "name": "Sms", "total": 150, "clicks": 35 },
    { "name": "Social Media", "total": 100, "clicks": 20 },
    { "name": "Website", "total": 100, "clicks": 15 }
  ]
}
```

#### Dashboard Summary Cards
- **URL**: `GET /analytics/summary`
- **Auth**: Admin Bearer Token
- **Response (200 OK)**:
```json
{
  "total_users": 150,
  "total_simulations": 20,
  "total_responses": 850,
  "accuracy_percentage": 80.0
}
```

#### Recent Response Activity
- **URL**: `GET /analytics/activity?limit=10&offset=0`
- **Auth**: Admin Bearer Token
- **Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "act-uuid-1",
      "user_email": "john.doe@company.com",
      "simulation_title": "Urgent Account Suspension Notice",
      "action": "reported",
      "is_correct": true,
      "created_at": "2026-01-15T09:00:00Z"
    }
  ],
  "total": 850
}
```

#### Users Security Directory
- **URL**: `GET /users/?page=1&page_size=10&search=john`
- **Auth**: Admin Bearer Token
- **Response (200 OK)**:
```json
{
  "data": [
    {
      "id": "u-1234",
      "full_name": "John Doe",
      "email": "john.doe@company.com",
      "department": "Finance",
      "risk_level": "high",
      "risk_score": 75.0,
      "completed_simulations": 8,
      "accuracy_percentage": 25.0
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```
*Users are automatically ordered by highest risk score first, with unassessed users at the bottom.*
