import os
import requests
from datetime import date

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
CRON_SECRET = os.environ["CRON_SECRET"]
WORDS_GENERATOR_URL = os.environ["WORDS_GENERATOR_URL"]

def handler(request, response):
    token = request.headers.get("x-cron-secret")
    if token != CRON_SECRET:
        return response.status(401).json({"error": "Unauthorized"})

    today = str(date.today())

    check_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        params={"solution_date": f"eq.{today}"}
    )

    existing = check_resp.json()
    if existing:
        return response.json({"message": f"Solution already exists for today: {existing[0]['solution']}"})

    word = requests.get(WORDS_GENERATOR_URL).json()[0].upper()

    insert_resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "solution": word,
            "solution_date": today,
            "created_at": today
        }
    )

    return response.json({"message": f"Word of the day ({today}) added: {word}", "status": insert_resp.status_code})
