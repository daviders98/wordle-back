from datetime import date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import WordsHistory
import requests
import os
from dotenv import load_dotenv
load_dotenv()

DICTIONARY_API = os.environ.get("DICTIONARY_API")

@api_view(['POST'])
def check_guess(request):
    """
    Expects JSON: { "guess": "APPLE" }
    Returns JSON: { "correct": true/false }
    """
    guess = request.data.get('guess', '').strip().upper()

    today_word = WordsHistory.objects.filter(solution_date=date.today()).first()
    if not today_word:
        return Response({"error": "Today's word not found."}, status=404)

    is_correct = guess == today_word.solution.upper()
    return Response({"correct": is_correct}, status=200)


@api_view(['POST'])
def validate_word(request):
    """
    Expects JSON: { "word": "STEAM" }
    Returns JSON: { "valid": true/false }
    Word is valid if it's in the dictionary API OR in the generator history.
    """
    word = request.data.get('word', '').strip().upper()

    in_generator = WordsHistory.objects.filter(solution__iexact=word).exists()

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
