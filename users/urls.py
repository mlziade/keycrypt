from django.urls import path
from .views import LoginView, LogoutView, ProfileView, RegisterView, ResetPasswordView, ChangePasswordView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/<uuid:reset_id>/', ChangePasswordView.as_view(), name='change_password'),
]