# ScamShield
Next.js frontend with a FastAPI companion service. Authentication runs through Supabase Auth. Guests can train without an account. The safety desk and tutorials are available in guest mode.

## Run locally
1. Use Node 22+ and Python 3.10+. At the project root run `npm ci`.
2. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local using your public Supabase URL and publishable key. Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 to use FastAPI. Leaving it unset uses Supabase directly with the same row ownership policies.
3. In backend/.env set SUPABASE_URL, SUPABASE_ANON_KEY and FRONTEND_ORIGIN=http://localhost:3000. The training API does not require a service role key.
4. Apply backend/migrations/001_training.sql in your Supabase project. In Supabase Auth, allow your dashboard redirect URL for email confirmation and Google OAuth. Google must already be enabled.
5. In backend, create a Python virtual environment, install requirements.txt and run `uvicorn app.main:app --port 8000`. At the project root run `npm run develop`. For one server, build with `npm run build` before starting FastAPI and use the same origin for the API.
6. Visit /login/ to create an account, sign in or continue as a guest. Guest training history stays in the browser. Authenticated history uses the API when configured. If cloud storage is unavailable the dashboard falls back to local history. Administrator assessment analytics use stored submissions.

## Uploaded backend compatibility
The uploaded README and integration guide describe a larger API. Its original app, migrations and tests were absent. This package includes the supplied Python utilities, dependencies and reference documentation plus a replacement service implementing /api/v1/health, /api/v1/auth/me, /api/v1/responses/ and /api/v1/responses/history for the four translated frontend scenarios. The original seed and verification scripts target additional tables in the original schema and are optional. Do not run the seed on an existing database without reviewing it.

## Simulation Arena
Open **Simulations** at /simulations/ after signing in. The Scenario library includes ten independently scored exercises and a combined field assessment. The Practice inbox preserves guest training. Assignments, Profile, Lab studio and Review share the same tab. Existing /arena/ bookmarks forward here. Start the self-paced field assessment or open an assigned lab. The administrator studio is available to accounts whose verified Supabase app_metadata.role is admin. Set this using your trusted Supabase administrator tooling. User-editable metadata does not grant privileges. Users enter the training roster on their first authenticated assessment request. In Lab studio an account administrator can grant or remove instructor access. Instructors can author and assign labs, update deadlines, review results and leave feedback. Account administrators also manage membership, batches and access. Authored labs can be edited until assignment, then saved as new versions.

The FastAPI process is required for the Arena. For same-origin hosting, set NEXT_PUBLIC_API_URL=/api/v1 before building, then start FastAPI after the build and visit its root URL. For separate frontend hosting, set the public API base URL at build time and set FRONTEND_ORIGIN on the backend. Serve production traffic over HTTPS. Store ARENA_DB on a persistent private volume (default backend/data/arena.sqlite) and back it up. Use one backend host for this SQLite configuration.

The Lab studio creates custom weighted multiple-choice assessments and assigns each lab once per learner, individually or by batch. Each started assignment can be resumed and submitted once before its deadline. The server measures elapsed wall-clock time including pauses. Manual release withholds scores, feedback and decision breakdowns. Review can release or withdraw results. Learner and administrator views refresh every 30 seconds and after writes. Analytics derive from stored attempts. The new Arena interface is in English.

### One-process localhost startup
With Python dependencies installed, put the existing public Supabase project URL and publishable key in the root .env.local file. For this mode set NEXT_PUBLIC_API_URL=/api/v1. From the project root run:

```sh
npm ci
npm run build
python run_local.py
```

Open http://127.0.0.1:8000/simulations/. The launcher binds to loopback and serves the frontend and backend together. Set a durable ARENA_DB path if assessment data should live outside the project folder. For the included integration suite, run `python -m pytest tests` from backend.
