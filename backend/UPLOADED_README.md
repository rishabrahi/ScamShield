# SCAM SHIELD — BACKEND API
### Think Before You Click.

Scam Shield is an enterprise-grade cybersecurity awareness and phishing simulation platform designed to educate users, evaluate organizational susceptibility to social engineering, and provide real-time risk intelligence.

This directory contains the complete Python/FastAPI backend API service.

---

## Architecture Overview

- **Framework**: FastAPI (Asynchronous Python 3.10+)
- **Validation**: Pydantic v2
- **Database**: Supabase (PostgreSQL with Row Level Security)
- **Authentication**: Supabase Auth + JWT Verification (HS256)
- **Rate Limiting**: SlowAPI
- **Testing**: Pytest, HTTPX, Unittest Mocking

```
backend/
├── app/
│   ├── main.py                     # Application entry point & router aggregation
│   ├── core/
│   │   ├── config.py               # Environment configuration settings
│   │   ├── dependencies.py         # FastAPI dependency injection & RBAC checks
│   │   ├── security.py             # JWT verification & password validation
│   │   └── supabase_client.py      # Supabase client singleton initialization
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py             # User registration, login, logout, me, refresh
│   │       ├── simulations.py      # Simulation catalog with safe fields & filtering
│   │       ├── responses.py        # Submission, backend correctness check, history
│   │       ├── analytics.py        # Admin aggregate metrics, charts, activity
│   │       ├── users.py            # Admin user directory, risk scores, performance
│   │       └── health.py           # Service and database connectivity health checks
│   ├── schemas/                    # Pydantic v2 request & response schemas
│   ├── services/                   # Business logic & database operations
│   └── utils/
├── migrations/
│   ├── 001_create_tables.sql       # PostgreSQL DDL, triggers, and RLS policies
│   └── 002_seed_simulations.sql    # 20 realistic phishing & legitimate scenarios
├── tests/                          # Full pytest test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_simulations.py
│   ├── test_responses.py
│   ├── test_analytics.py
│   ├── test_users.py
│   └── test_health.py
├── .env.example
├── requirements.txt
├── API_INTEGRATION_GUIDE.md
└── README.md
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- A Supabase project (free tier is fully compatible)

### 2. Environment Setup

Create and activate a virtual environment:

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the template and configure your keys:

```bash
cp .env.example .env
```

Edit `.env` with your project credentials:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase Project URL (`https://xyz.supabase.co`) |
| `SUPABASE_ANON_KEY` | Supabase Anonymous Client Public Key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Secret Key (Server-only) |
| `JWT_SECRET` | Supabase Project JWT Secret (from API settings) |
| `FRONTEND_ORIGIN` | Allowed CORS origin (default: `http://localhost:5173`) |
| `API_ENV` | `development` or `production` |

---

## Database Migrations

In your Supabase project dashboard:
1. Open the **SQL Editor**.
2. Run `migrations/001_create_tables.sql`:
   - Creates `profiles`, `simulations`, and `user_responses` tables.
   - Configures PostgreSQL triggers to auto-create user profiles on Supabase Auth sign-ups.
   - Enables Row Level Security (RLS) on all tables.
3. Run `migrations/002_seed_simulations.sql`:
   - Populates 20 diverse, realistic phishing and legitimate scenarios across email, SMS, social media, and web vectors.

---

## Running the Server

Start the API with Uvicorn auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API documentation is automatically accessible at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints Reference

### Health
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | None | API service status |
| `GET` | `/api/v1/health/db` | None | Database connection probe |

### Authentication
| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | None | Register new user account |
| `POST` | `/api/v1/auth/login` | None | Authenticate with credentials |
| `POST` | `/api/v1/auth/logout` | Bearer Token | Invalidate current session |
| `GET` | `/api/v1/auth/me` | Bearer Token | Retrieve authenticated user profile |
| `POST` | `/api/v1/auth/refresh` | None | Refresh access token using refresh token |

### Simulations
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/simulations/` | Bearer Token | List simulations (excludes `is_phishing`) |

*Query Parameters: `exclude`, `difficulty` (`easy`, `medium`, `hard`), `attack_type` (`email`, `sms`, `social_media`, `website`, `phone`), `page`, `page_size`.*

### Responses
| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/responses/` | Bearer Token | Submit simulation action & compute correctness |
| `GET` | `/api/v1/responses/history` | Bearer Token | List current user's past response history |

### Analytics (Admin Only)
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/analytics/` | Admin Token | Detailed organizational analytics & chart metrics |
| `GET` | `/api/v1/analytics/summary` | Admin Token | Summary statistics for dashboard KPI cards |
| `GET` | `/api/v1/analytics/activity` | Admin Token | Live simulation response event feed |

### Users
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/users/` | Admin Token | User directory with risk scores and accuracy |
| `GET` | `/api/v1/users/me/performance` | Bearer Token | Current user's awareness performance profile |

---

## Business Logic & Risk Calculation

### Simulation Evaluation Matrix
Correctness is calculated strictly on the backend:

| Simulation Type | User Action | Result |
|---|---|---|
| **Phishing** (`is_phishing = true`) | `reported` | **Correct** (`true`) |
| **Phishing** (`is_phishing = true`) | `clicked` | **Incorrect** (`false`) |
| **Phishing** (`is_phishing = true`) | `ignored` | **Incorrect** (`false`) |
| **Legitimate** (`is_phishing = false`) | `reported` | **Incorrect** (`false`) |
| **Legitimate** (`is_phishing = false`) | `clicked` | **Correct** (`true`) |
| **Legitimate** (`is_phishing = false`) | `ignored` | **Correct** (`true`) |

### Vulnerability Risk Scoring Formula
The risk score assesses user vulnerability to cyber deception:
- **Sample Size Threshold**: If a user has completed fewer than **3 simulations**, the risk score is classified as **`unassessed`** (`score = 0.0` / insufficient baseline data).
- **Formula**:
  $$\text{Risk Score} = \left(\frac{\text{Incorrect Responses}}{\text{Total Completed Simulations}}\right) \times 100$$
- **Classifications**:
  - `0 - 30`: **Low Risk** (Resilient security posture)
  - `31 - 60`: **Medium Risk** (Moderate susceptibility; targeted reinforcement suggested)
  - `61 - 100`: **High Risk** (Critical vulnerability; immediate training required)

---

## Testing

Run the comprehensive automated test suite with pytest:

```bash
cd backend
pytest -v
```
