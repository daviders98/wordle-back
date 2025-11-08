from datetime import date, datetime, timedelta, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import os
import requests
import jwt
from .decorators import jwt_required
from dotenv import load_dotenv
from django_ratelimit.decorators import ratelimit

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
@ratelimit(key='ip', rate='20/m', block=True)
def guess_word(request):
    """
    Combined endpoint:
    1.- Validates word against Supabase and dictionary API.
    2.- If invalid: returns { valid: false }.
    3.- If valid: compares with today's solution and returns { valid: true, letters: [...] }.
    """
    guess = request.data.get('guess', '').strip().upper()
    if len(guess) != 5 or not guess.isalpha():
        return Response({"valid": False, "error": "Invalid word length or characters."}, status=400)
    # Step 1
    validation_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers=HEADERS,
        params={"select": "solution", "solution": f"eq.{guess}"}
    )
    data = validation_resp.json()
    in_generator = len(data) > 0

    is_valid = False
    if in_generator:
        is_valid = True
    else:
        try:
            dict_resp = requests.get(DICTIONARY_API + guess.lower())
            if dict_resp.status_code == 200:
                is_valid = True
        except requests.RequestException:
            is_valid = False

    if not is_valid:
        return Response({"valid": False}, status=200)

    # Step 2
    today = date.today().isoformat()
    word_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers=HEADERS,
        params={"select": "solution", "solution_date": f"eq.{today}"}
    )
    word_data = word_resp.json()

    if not word_data:
        return Response({"error": "Today's word not found."}, status=404)

    solution = word_data[0]["solution"].upper()
    result = [0] * len(guess)
    solution_letters_remaining = list(solution)

    # Step 3 First pass: correct position
    for i in range(min(len(guess), len(solution))):
        if guess[i] == solution[i]:
            result[i] = 2
            solution_letters_remaining[i] = None

    # Step 3 Second pass: wrong position but in word
    for i in range(len(guess)):
        if result[i] == 0 and guess[i] in solution_letters_remaining:
            result[i] = 1
            solution_letters_remaining[solution_letters_remaining.index(guess[i])] = None

    return Response({"valid": True, "letters": result}, status=200)

@api_view(['POST'])
def get_jwt(request):
    """Simple JWT generator"""
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return Response({"token": token})

def health_check(request):
    return JsonResponse({"status": "ok"})

@api_view(["GET"])
def list_words(request):
    """Returns all past words (before today)."""
    today = date.today().isoformat()

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/words_history",
        headers=HEADERS,
        params={
            "select": "solution,solution_date,solution_number",
            "solution_date": f"lt.{today}",
            "order": "solution_date.desc"
        },
    )

    if response.status_code != 200:
        return Response(
            {"error": "Failed to fetch words from Supabase"},
            status=response.status_code,
        )

    return Response(response.json(), status=200)