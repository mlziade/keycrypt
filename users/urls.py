from django.urls import path
from .views import ProfileLoginView, ProfileLogoutView

app_name = 'users'

urlpatterns = [
    path('login/', ProfileLoginView.as_view(), name='login'),
    path('logout/', ProfileLogoutView.as_view(), name='logout'),
]