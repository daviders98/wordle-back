from django.urls import path
from .views import check_guess, validate_word, get_jwt

urlpatterns = [
    path('check-guess/', check_guess),
    path('validate-word/', validate_word),
    path('get-jwt/', get_jwt),
]
