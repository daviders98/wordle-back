import os
import json
import base64
import random
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
CRON_SECRET = os.environ["CRON_SECRET"]

AES_KEY  = os.environ["WORDLE_AES_KEY"].encode()
AES_IV = os.environ["WORDLE_AES_IV"].encode()

ENCRYPTED_FILE = "wordle_back/words_encrypted.bin"


def load_words():
    """Decrypt and return the word list."""
    with open(ENCRYPTED_FILE, "rb") as f:
        encrypted = f.read()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV))
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()

    # Strip PKCS7 padding
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]

    return json.loads(decrypted.decode("utf-8"))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Serverless function start")

        token = self.headers.get("x-cron-secret")
        if token != CRON_SECRET:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return

        words = load_words()
        word = random.choice(words).upper()
        latest_resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/words_history",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            params={
                "select": "*",
                "order": "solution_date.desc",
                "limit": 1
            }
        )

        latest_data = latest_resp.json()
        if latest_data:
            last_entry = latest_data[0]
            next_date = (datetime.strptime(last_entry["solution_date"], "%Y-%m-%d") + timedelta(days=1)).date()
            next_solution_number = last_entry.get("solution_number", 0) + 1
        else:
            next_date = datetime.today().date()
            next_solution_number = 1

        insert_resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/words_history",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "solution": word,
                "solution_date": str(next_date),
                "solution_number": next_solution_number
            }
        )

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            f'{{"message": "Word added for {next_date}: {word}", "solution_number": {next_solution_number}, "status": {insert_resp.status_code}}}'.encode()
        )
