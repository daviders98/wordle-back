import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "wordle_back/words_with_meanings.json"
ENCRYPTED_FILE = "wordle_back/words_encrypted.bin"

KEY = os.environ["WORDLE_AES_KEY"].encode()
IV = os.environ["WORDLE_AES_IV"].encode()

if len(KEY) != 32:
    raise ValueError("KEY must be 32 bytes")
if len(IV) != 16:
    raise ValueError("IV must be 16 bytes")

print("🔐 Encrypting enriched word list")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)
print("JSON length:", len(json_str))

cipher = AES.new(KEY, AES.MODE_CBC, IV)
encrypted = cipher.encrypt(pad(json_str.encode("utf-8"), AES.block_size))

with open(ENCRYPTED_FILE, "wb") as f:
    f.write(encrypted)

print("✅ Encrypted file written:", ENCRYPTED_FILE)
print("File size:", os.path.getsize(ENCRYPTED_FILE))
