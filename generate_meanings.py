import os
import json
import time
import requests
from decrypt import decrypt_words
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
OUTPUT_FILE = "wordle_back/words_with_meanings.json"
MODEL = "llama3"
SAVE_EVERY = 25 # checkpoint every N words
DELAY = 0.2 # seconds between AI calls
# =========================================

def get_meaning(word: str) -> str:
    prompt = (
        f"Give a short, simple dictionary-style definition of the word "
        f"'{word}'. One sentence. No examples."
    )

    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        },
        timeout=30
    )

    text = r.json()["response"].strip()

    if "." in text:
        text = text.split(".", 1)[0] + "."

    return text

def main():
    words = decrypt_words()
    print(f"🔓 Decrypted {len(words)} words")

    results = []
    completed = set()

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            results = json.load(f)
            completed = {item["word"] for item in results}
        print(f"↩️ Resuming from {len(completed)} words")

    for i, word in enumerate(words, 1):
        word = word.upper()
        if word in completed:
            continue

        print(f"{i}/{len(words)} → {word}")
        meaning = get_meaning(word)

        results.append({
            "word": word,
            "meaning": meaning
        })

        if i % SAVE_EVERY == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)
            print("💾 checkpoint saved")

        time.sleep(DELAY)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Done! Meanings generated.")

if __name__ == "__main__":
    main()
