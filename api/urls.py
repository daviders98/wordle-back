from django.urls import path
from . import views

urlpatterns = [
    path('check/', views.check_guess, name='check_guess'),
    path('validate/', views.validate_word, name='validate_word'),
]