from django.urls import path
from .views import SolveCurrentDailyPuzzleView, CreateDailyPuzzleView, DailyLeaderboardView, ListPreviousDailyPuzzlesView, SolvePreviousDailyPuzzleView, ViewDailySolutionView, trigger_daily_challenge

app_name = 'daily'

urlpatterns = [
    path('daily-challenge/', SolveCurrentDailyPuzzleView.as_view(), name='solve_daily_puzzle'),
    path('create/', CreateDailyPuzzleView.as_view(), name='daily_challenge_create'),
    path('admin/trigger-daily-challenge/', trigger_daily_challenge, name='trigger_daily_challenge'),
    path('leaderboard/', DailyLeaderboardView.as_view(), name='daily_leaderboard'),
    path('previous/', ListPreviousDailyPuzzlesView.as_view(), name='list_previous_puzzles'),
    path('previous/<uuid:puzzle_id>/', SolvePreviousDailyPuzzleView.as_view(), name='solve_previous_puzzle'),
    path('solution/<uuid:puzzle_id>/', ViewDailySolutionView.as_view(), name='view_solution'),
]