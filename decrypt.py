# decrypt.py
import os
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from dotenv import load_dotenv

load_dotenv()

ENCRYPTED_FILE = "wordle_back/words_encrypted.bin"
AES_KEY = os.environ["WORDLE_AES_KEY"].encode()
AES_IV = os.environ["WORDLE_AES_IV"].encode()

def decrypt_words():
    """Decrypt and return the word list."""
    with open(ENCRYPTED_FILE, "rb") as f:
        encrypted = f.read()

    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = cipher.decrypt(encrypted)
    decrypted = unpad(padded, AES.block_size)

    return json.loads(decrypted.decode("utf-8"))


if __name__ == "__main__":
    words = decrypt_words()
    print(f"🔓 Decrypted {len(words)} words")
    print("Sample:", words[:5])
