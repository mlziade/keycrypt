from django.urls import path
from .views import CreatePuzzleView, ViewPuzzleView, SolvePuzzleView, solve_question

app_name = 'puzzle'

urlpatterns = [
    path('create/', CreatePuzzleView.as_view(), name='create_puzzle'),
    path('view/<int:puzzle_id>/', ViewPuzzleView.as_view(), name='view_puzzle'),
    path('solve/<int:puzzle_id>/', SolvePuzzleView.as_view(), name='solve_puzzle'),
    path('solve_question/<int:puzzle_id>/<int:question_id>/', solve_question, name='solve_question'),
]