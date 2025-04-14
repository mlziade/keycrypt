from django.urls import path
from .views import ProfileLoginView, ProfileLogoutView, ProfileView, RegisterView

app_name = 'users'

urlpatterns = [
    path('login/', ProfileLoginView.as_view(), name='login'),
    path('logout/', ProfileLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
]