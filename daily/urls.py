from django.urls import path
from .views import SolveDailyPuzzleView, CreateDailyPuzzleView

app_name = 'daily'

urlpatterns = [
    path('daily-challenge/', SolveDailyPuzzleView.as_view(), name='solve_daily_puzzle'),
    path('create/', CreateDailyPuzzleView.as_view(), name='daily_challenge_create'),
]