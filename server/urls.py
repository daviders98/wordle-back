from django.urls import path
from .views import check_guess, validate_word, get_jwt, health_check, list_words

urlpatterns = [
    path('guess_word/', guess_word),
    path('get-jwt/', get_jwt),
    path("health/", health_check),
    path("list/",list_words)
]
