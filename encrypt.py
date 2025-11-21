import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "wordle_back/words.json"
ENCRYPTED_FILE = "wordle_back/words_encrypted.bin"

KEY = os.environ.get("WORDLE_AES_KEY")  # must be 32 bytes for AES-256
IV = os.environ.get("WORDLE_AES_IV")    # must be 16 bytes

print("=== LOADING ENV VARS ===")
print("KEY present:", bool(KEY))
print("IV present:", bool(IV))

if not KEY or not IV:
    raise ValueError("Environment variables WORDLE_AES_KEY and WORDLE_AES_IV are required.")

KEY = KEY.encode()
IV = IV.encode()

# LOG lengths
print("KEY length:", len(KEY))
print("IV length:", len(IV))
if len(KEY) != 32:
    print("❌ ERROR: KEY must be 32 bytes!")
if len(IV) != 16:
    print("❌ ERROR: IV must be 16 bytes!")

print("\n=== READING INPUT JSON ===")
print("File exists:", os.path.exists(INPUT_FILE))

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    words = json.load(f)

print("Original word count:", len(words))

# --- CLEAN DATA --- #
words = [w.lower().strip() for w in words]
words = [w for w in words if len(w) == 5 and w.isalpha()]
unique = sorted(set(words))

print("Cleaned word count:", len(unique))
print("Duplicates removed:", len(words) - len(unique))

clean_json_str = json.dumps(unique)
print("JSON string length:", len(clean_json_str))

print("\n=== ENCRYPTING ===")
cipher = AES.new(KEY, AES.MODE_CBC, IV)
encrypted_bytes = cipher.encrypt(pad(clean_json_str.encode(), AES.block_size))

print("Encrypted bytes length:", len(encrypted_bytes))
print("Block size:", AES.block_size)

with open(ENCRYPTED_FILE, "wb") as f:
    f.write(encrypted_bytes)

print("\n=== SUCCESS ===")
print(f"Encrypted file written to: {ENCRYPTED_FILE}")
print("File size on disk:", os.path.getsize(ENCRYPTED_FILE))
