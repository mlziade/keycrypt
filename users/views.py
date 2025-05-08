from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import QuerySet
from django.utils.timezone import now

from .models import Profile, ResetPasswordLink
from .forms import CreateUserForm, RequestResetLinkForm, ResetPasswordForm
from .send_email import send_reset_password_email

from puzzle.models import Puzzle, PuzzleSolved
from daily.models import DailyChallenge

class LoginView(View):
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

class LogoutView(View):
    @method_decorator(login_required(login_url='users:login'))
    def post(self, request):
        logout(request)
        return redirect('home')

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        form = CreateUserForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = Profile.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            login(request, user)
            return redirect('home')
        else:
            # If passwords don't match or other validation fails, form errors will be displayed
            return render(request, 'register.html', {'form': form})

class ProfileView(View):
    @method_decorator(login_required(login_url='users:login'))
    def get(self, request):
        profile: Profile = request.user

        user_created_puzzles: QuerySet[Puzzle] = Puzzle.objects.filter(created_by=profile)
        solved_puzzles: QuerySet[Puzzle] = Puzzle.objects.filter(solved_puzzles__solved_by=profile)
        solved_daily_challenges: QuerySet[DailyChallenge] = DailyChallenge.objects.filter(solved_puzzles__solved_by=profile)

        return render(request, 'user_profile.html', {
            'profile': profile,
            'user_created_puzzles': user_created_puzzles,
            'solved_puzzles': solved_puzzles,
            'solved_daily_challenges': solved_daily_challenges,
        })

class ResetPasswordView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        form: RequestResetLinkForm = RequestResetLinkForm()

        return render(request, 'reset_password.html', {
            'form': form,
        })

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        form: RequestResetLinkForm = RequestResetLinkForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user: Profile = Profile.objects.get(email=email)
                if not user:
                    form.add_error('email', 'Email address not found.')
                    return render(request, 'reset_password.html', {'form': form})
                
                reset_link: ResetPasswordLink = ResetPasswordLink.objects.create(user=user)

                # send email with the reset link
                send_reset_password_email(
                    reset_id=reset_link.id,
                    user_email=user.email,
                    username=user.username
                )

                return redirect('users:login')
            except Profile.DoesNotExist:
                form.add_error('email', 'Email address not found.')
        return redirect('home')

class ChangePasswordView(View):
    def get(self, request, reset_id):
        if request.user.is_authenticated:
            return redirect('home')
        
        # Check if the reset link is valid and not expired
        reset_link: ResetPasswordLink = ResetPasswordLink.objects.get(id=reset_id)

        if reset_link.expires_at < now():
            return redirect('users:reset_password')
    
        if reset_link.is_used:
            return redirect('users:reset_password')
        
        form: ResetPasswordForm = ResetPasswordForm()

        return render(request, 'change_password.html', {
            'reset_link': reset_link,
            'form': ResetPasswordForm(),
        })

    def post(self, request, reset_id):
        if request.user.is_authenticated:
            return redirect('home')
        
        # Check if the reset link is valid and not expired
        reset_link: ResetPasswordLink = ResetPasswordLink.objects.get(id=reset_id)

        if reset_link.expires_at < now():
            return redirect('users:reset_password')
        
        if reset_link.is_used:
            return redirect('users:reset_password')
        
        try:
            form: ResetPasswordForm = ResetPasswordForm(request.POST)
            
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                reset_link.user.set_password(new_password)
                reset_link.user.save()
                reset_link.is_used = True
                reset_link.save()
                
                # Logic to send a confirmation email
                return redirect('users:login')
            else:
                # If passwords don't match or other validation fails, form errors will be displayed
                return render(request, 'change_password.html', {
                    'reset_link': reset_link,
                    'form': form,
                })
        except ResetPasswordLink.DoesNotExist:
            # Handle the case where the reset link does not exist
            return redirect('users:reset_password')