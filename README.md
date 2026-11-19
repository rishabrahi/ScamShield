# ScamShield
Next.js frontend with a FastAPI companion service. Authentication runs through Supabase Auth. Guests can train without an account. The safety desk and tutorials are available in guest mode.

## Run locally
1. Use Node 22+ and Python 3.10+. At the project root run `npm ci`.
2. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local using your public Supabase URL and publishable key. Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 to use FastAPI. Leaving it unset uses Supabase directly with the same row ownership policies.
3. In backend/.env set SUPABASE_URL, SUPABASE_ANON_KEY and FRONTEND_ORIGIN=http://localhost:3000. The training API does not require a service role key.
4. Apply backend/migrations/001_training.sql in your Supabase project. In Supabase Auth, allow your dashboard redirect URL for email confirmation and Google OAuth. Google must already be enabled.
5. In backend, create a Python virtual environment, install requirements.txt and run `uvicorn app.main:app --port 8000`. At the project root run `npm run develop`. For one server, build with `npm run build` before starting FastAPI and use the same origin for the API.
6. Visit /login/ to create an account, sign in or continue as a guest. Guest training history stays in the browser. Authenticated history uses the API when configured. If cloud storage is unavailable the dashboard falls back to local history. Admin analytics use illustrative data.

## Uploaded backend compatibility
The uploaded README and integration guide describe a larger API. Its original app, migrations and tests were absent. This package includes the supplied Python utilities, dependencies and reference documentation plus a replacement service implementing /api/v1/health, /api/v1/auth/me, /api/v1/responses/ and /api/v1/responses/history for the four translated frontend scenarios. The original seed and verification scripts target additional tables in the original schema and are optional. Do not run the seed on an existing database without reviewing it.
