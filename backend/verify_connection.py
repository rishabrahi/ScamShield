"""
Scam Shield - Backend & Database Connection Verification Script
Run this script to verify your Supabase configuration and database tables.
Usage:
    python verify_connection.py
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


def print_status(step: str, success: bool, message: str = ""):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {step}")
    if message:
        print(f"   └── {message}")


def run_checks():
    print("=" * 65)
    print("  SCAM SHIELD — BACKEND & DATABASE VERIFICATION")
    print("=" * 65)
    print()

    # --- 1. Check .env file ---
    if not env_path.exists():
        print_status(".env Configuration File", False, f"File not found at {env_path}")
        print("\n👉 ACTION REQUIRED:")
        print("   Create a .env file in the 'backend' folder by copying .env.example:")
        print("   cp .env.example .env")
        print("   Then open .env and fill in your Supabase credentials.\n")
        return False

    print_status(".env Configuration File", True, f"Found at {env_path}")

    # --- 2. Check variables presence ---
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    jwt_secret = os.getenv("JWT_SECRET", "").strip()

    missing = []
    if not supabase_url or "your-project" in supabase_url:
        missing.append("SUPABASE_URL")
    if not supabase_anon_key or "your-anon-key" in supabase_anon_key:
        missing.append("SUPABASE_ANON_KEY")
    if not supabase_service_key or "your-service-role-key" in supabase_service_key:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not jwt_secret or "your-supabase-jwt-secret" in jwt_secret:
        missing.append("JWT_SECRET")

    if missing:
        print_status("Environment Variables", False, f"Missing or placeholder values for: {', '.join(missing)}")
        print("\n👉 ACTION REQUIRED:")
        print("   Open backend/.env and replace placeholders with your actual Supabase keys.\n")
        return False

    print_status("Environment Variables", True, f"URL: {supabase_url[:30]}...")

    # --- 3. Test Supabase Client Connection ---
    print("\nConnecting to Supabase...")
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_service_key)
        print_status("Supabase Client Initialization", True)
    except Exception as e:
        print_status("Supabase Client Initialization", False, str(e))
        return False

    # --- 4. Test Table Connectivity ---
    all_tables_ok = True
    tables = ["profiles", "simulations", "user_responses"]

    for table in tables:
        try:
            res = client.table(table).select("id", count="exact").limit(1).execute()
            count = res.count if res.count is not None else len(res.data or [])
            print_status(f"Table '{table}'", True, f"Accessible (records found: {count})")
        except Exception as e:
            all_tables_ok = False
            error_msg = str(e)
            if "relation" in error_msg.lower() or "does not exist" in error_msg.lower():
                print_status(f"Table '{table}'", False, "Table does NOT exist in Supabase database")
            else:
                print_status(f"Table '{table}'", False, error_msg)

    if not all_tables_ok:
        print("\n👉 ACTION REQUIRED:")
        print("   The database tables are missing. To create them:")
        print("   1. Open your Supabase Dashboard -> SQL Editor")
        print("   2. Run 'migrations/001_create_tables.sql'")
        print("   3. Run 'migrations/002_seed_simulations.sql'\n")
        return False

    # --- 5. Test Simulations Seed Data ---
    try:
        sim_res = client.table("simulations").select("id", count="exact").execute()
        count = sim_res.count if sim_res.count is not None else len(sim_res.data or [])
        if count == 0:
            print_status("Simulations Seed Data", False, "Table is empty (0 scenarios)")
            print("\n👉 ACTION REQUIRED:")
            print("   Run 'migrations/002_seed_simulations.sql' in the Supabase SQL Editor to load the 20 simulation scenarios.\n")
        else:
            print_status("Simulations Seed Data", True, f"{count} phishing scenarios ready for training")
    except Exception as e:
        print_status("Simulations Seed Data", False, str(e))

    print("\n" + "=" * 65)
    print("  RESULT: BACKEND & DATABASE FULLY OPERATIONAL! 🎉")
    print("=" * 65 + "\n")
    return True


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
