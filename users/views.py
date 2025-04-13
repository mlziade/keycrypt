from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm

from .models import Profile

class ProfileLoginView(View):
    def get(self, request):
        form = AuthenticationForm(request=request, data=None)        
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form: AuthenticationForm = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user: Profile = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            # Form is not valid, show form with errors
            return render(request, 'login.html', {'form': form})

class ProfileLogoutView(View):
    @method_decorator(login_required(login_url='users:login'))
    def post(self, request):
        logout(request)
        return redirect('home')