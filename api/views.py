from datetime import date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import WordsHistory

@api_view(['POST'])
def check_guess(request):
    """
    Expects JSON: { "guess": "APPLE" }
    Returns JSON: { "correct": true/false }
    """
    guess = request.data.get('guess','').strip().upper()

    today_word = WordsHistory.objects.filter(solution_date=date.today()).first()
    if not today_word:
        return Response({"error": "Today's word not found."}, status=404)

    is_correct = guess == today_word.solution.upper()
    return Response({"correct": is_correct},status=200)
