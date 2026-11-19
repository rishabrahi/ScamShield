"""Serve the exported frontend and FastAPI together on localhost."""
import os
import sys
from pathlib import Path

import uvicorn
from dotenv import dotenv_values, load_dotenv

root = Path(__file__).resolve().parent
if not (root / "out" / "simulations" / "index.html").is_file():
    sys.exit("Build the frontend first with npm ci and npm run build.")
load_dotenv(root / "backend" / ".env")
frontend = dotenv_values(root / ".env.local")
for key in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):
    value = frontend.get("NEXT_PUBLIC_" + key)
    if value:
        os.environ.setdefault(key, value)
    if not os.getenv(key):
        sys.exit(f"Set {key} in backend/.env or NEXT_PUBLIC_{key} in .env.local.")
sys.path.insert(0, str(root / "backend"))
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
