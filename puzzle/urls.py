from django.urls import path
from .views import CreatePuzzleView

app_name = 'puzzle'

urlpatterns = [
    path('create/', CreatePuzzleView.as_view(), name='create_puzzle'),
]