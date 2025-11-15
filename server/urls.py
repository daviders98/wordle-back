from django.urls import path
from django.http import JsonResponse
from .views import guess_word, get_jwt, health_check, list_words

def custom_404(request, exception):
    return JsonResponse({"error": "Endpoint not found"}, status=404)

urlpatterns = [
    path('guess-word/', guess_word),
    path('get-jwt/', get_jwt),
    path("health/", health_check),
    path("list/", list_words),
]

handler404 = custom_404
