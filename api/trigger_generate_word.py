import os
import requests
from http.server import BaseHTTPRequestHandler

GENERATE_WORD_URL = os.environ.get("GENERATE_WORD_URL")
CRON_SECRET = os.environ.get("CRON_SECRET")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Trigger function start")

        resp = requests.get(
            GENERATE_WORD_URL,
            headers={"x-cron-secret": CRON_SECRET}
        )

        self.send_response(resp.status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(resp.content)
