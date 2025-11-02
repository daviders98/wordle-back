import os
import requests
from datetime import date
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
CRON_SECRET = os.environ["CRON_SECRET"]
WORDS_GENERATOR_URL = os.environ["WORDS_GENERATOR_URL"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('Serverless function start')
        token = self.headers.get("x-cron-secret")
        if token != CRON_SECRET:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

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
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                f'{{"message": "Solution already exists for today: {existing[0]["solution"]}"}}'.encode("utf-8")
            )
            return

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

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            f'{{"message": "Word of the day ({today}) added: {word}", "status": {insert_resp.status_code}}}'.encode("utf-8")
        )
