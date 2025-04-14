from django.urls import path
from .views import CreatePuzzleView, ViewPuzzleView, SolvePuzzleView, MyPuzzlesView, test_question

app_name = 'puzzle'

urlpatterns = [
    path('create/', CreatePuzzleView.as_view(), name='create_puzzle'),
    path('view/<uuid:puzzle_id>/', ViewPuzzleView.as_view(), name='view_puzzle'),
    path('solve/<uuid:puzzle_id>/', SolvePuzzleView.as_view(), name='solve_puzzle'),
    path('my_puzzles/', MyPuzzlesView.as_view(), name='my_puzzles'),
    path('test_question/<uuid:puzzle_id>/<uuid:question_id>/', test_question, name='test_question'),
]