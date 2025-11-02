from datetime import date, datetime, timedelta, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import os
import requests
import jwt
from .decorators import jwt_required
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
DICTIONARY_API = os.environ.get("DICTIONARY_API")

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = int(os.environ.get('JWT_EXP_DELTA_SECONDS', 3600))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

@api_view(['POST'])
@jwt_required
def check_guess(request):
    """
    Expects JSON: { "guess": "APPLE" }
    Returns JSON: { "letters": [0,1,2,...] }
    0 = not in word
    1 = in word, wrong position
    2 = correct position
    """
    guess = request.data.get('guess', '').strip().upper()

    today = date.today().isoformat()
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers=HEADERS,
        params={"select": "solution", "solution_date": f"eq.{today}"}
    )
    data = response.json()
    if not data:
        return Response({"error": "Today's word not found."}, status=404)

    solution = data[0]["solution"].upper()
    result = [0] * len(guess)
    solution_letters_remaining = list(solution)
    
    # First pass: correct letters in correct position
    for i in range(min(len(guess), len(solution))):
        if guess[i] == solution[i]:
            result[i] = 2
            solution_letters_remaining[i] = None  # mark as used

    # Second pass: correct letters in wrong position
    for i in range(len(guess)):
        if result[i] == 0 and guess[i] in solution_letters_remaining:
            result[i] = 1
            solution_letters_remaining[solution_letters_remaining.index(guess[i])] = None

    return Response({"letters": result}, status=200)

@api_view(['POST'])
@jwt_required
def validate_word(request):
    """
    Expects JSON: { "word": "STEAM" }
    Returns JSON: { "valid": true/false }
    Word is valid if it's in the Supabase table word_history or the dictionary API.
    """
    word = request.data.get('word', '').strip().upper()

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers=HEADERS,
        params={"select": "solution", "solution": f"eq.{word}"}
    )
    data = response.json()
    in_generator = len(data) > 0

    is_valid = False
    if in_generator:
        is_valid = True
    else:
        try:
            resp = requests.get(DICTIONARY_API + word.lower())
            if resp.status_code == 200:
                is_valid = True
        except requests.RequestException:
            is_valid = False

    return Response({"valid": is_valid}, status=200)

@api_view(['POST'])
def get_jwt(request):
    """
    Simple JWT generator.
    Returns: { "token": "..." }
    """
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return Response({"token": token})

def health_check(request):
    return JsonResponse({"status": "ok"})