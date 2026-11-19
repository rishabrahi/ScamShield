"""ScamShield API. Supabase validates bearer tokens and applies ownership policies."""
import os
from pathlib import Path
from urllib.parse import urlencode
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
app = FastAPI(title="ScamShield")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")], allow_methods=["GET","POST"], allow_headers=["Content-Type","Authorization"])

class Attempt(BaseModel):
    id: int = Field(ge=0, le=3)
    decision: bool
    time: int = Field(gt=0)

async def forward(method, path, token, payload=None):
    if not token.startswith("Bearer "):
        raise HTTPException(401, "Sign in required")
    headers = {"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": token}
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            response = await client.request(method, os.environ["SUPABASE_URL"].rstrip("/") + path, headers=headers, json=payload)
        except httpx.RequestError:
            raise HTTPException(503, "Database unavailable")
    if response.is_error:
        raise HTTPException(response.status_code, "Request could not be completed")
    return response.json() if response.content else {}

@app.get("/api/v1/health")
def health():
    return {"status":"ok"}

@app.get("/api/v1/auth/me")
async def me(authorization: str = Header(default="")):
    return await forward("GET","/auth/v1/user",authorization)

@app.get("/api/v1/responses/history")
async def history(authorization: str = Header(default="")):
    rows = await forward("GET","/rest/v1/scamshield_attempts?select=lesson,decision,time_ms&order=time_ms.asc",authorization)
    return [{"id":r["lesson"],"decision":r["decision"],"time":r["time_ms"]} for r in rows]

@app.post("/api/v1/responses/",status_code=201)
async def submit(entry: Attempt, authorization: str = Header(default="")):
    await forward("POST","/rest/v1/scamshield_attempts",authorization,{"lesson":entry.id,"decision":entry.decision,"time_ms":entry.time})
    return {"success":True}

if (ROOT.parent / "out").is_dir():
    app.mount("/",StaticFiles(directory=ROOT.parent / "out",html=True),name="site")
