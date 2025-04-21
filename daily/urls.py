from django.urls import path
from .views import SolveDailyPuzzleView, CreateDailyPuzzleView, DailyLeaderboardView, trigger_daily_challenge

app_name = 'daily'

urlpatterns = [
    path('daily-challenge/', SolveDailyPuzzleView.as_view(), name='solve_daily_puzzle'),
    path('create/', CreateDailyPuzzleView.as_view(), name='daily_challenge_create'),
    path('admin/trigger-daily-challenge/', trigger_daily_challenge, name='trigger_daily_challenge'),
    path('leaderboard/', DailyLeaderboardView.as_view(), name='daily_leaderboard'),
]