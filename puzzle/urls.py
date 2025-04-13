from django.urls import path
from .views import CreatePuzzleView, ViewPuzzleView

app_name = 'puzzle'

urlpatterns = [
    path('create/', CreatePuzzleView.as_view(), name='create_puzzle'),
    path('view/<int:puzzle_id>/', ViewPuzzleView.as_view(), name='view_puzzle'),
]