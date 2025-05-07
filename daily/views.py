import datetime
from django.shortcuts import render, redirect
from django.db.models import QuerySet
from django.db import models
from django.views import View
from django.core import management
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import DailyChallenge
from .forms import CreateDailyPuzzleForm

from puzzle.models import PuzzleQuestion, PuzzleQuestionHint, PuzzleSolved
from puzzle.forms import CreatePuzzleQuestionsFormSet
from puzzle.services import encrypt_message, decrypt_message

from users.models import Profile

class CreateDailyPuzzleView(View):
    def get(self, request):
        # Render the form for creating a daily puzzle
        form = CreateDailyPuzzleForm()
        question_formset = CreatePuzzleQuestionsFormSet(prefix='questions')

        return render(request, 'admin_create_daily.html', {
            'form': form,
            'question_formset': question_formset
        })
    
    def post(self, request):
        form = CreateDailyPuzzleForm(request.POST)
        question_formset = CreatePuzzleQuestionsFormSet(request.POST, prefix='questions')

        if form.is_valid() and question_formset.is_valid():
            # Save the daily challenge
            daily_challenge = form.save(commit=False)
            daily_challenge.created_by = request.user
            daily_challenge.save()

            if len(question_formset) == 0:
                messages.error(request, "Please add at least one question.")
                return render(request, 'admin_create_daily.html', {
                    'form': form,
                    'question_formset': question_formset,
                })

            solutions: list[str] = []
            # Process the questions formset
            for question_form in question_formset:
                if question_form.cleaned_data:
                    question_text = question_form.cleaned_data.get('question')
                    solution_text = question_form.cleaned_data.get('solution')
                    hint_text = question_form.cleaned_data.get('hint', '')

                    if question_text and solution_text:
                        question = PuzzleQuestion(
                            puzzle=daily_challenge,
                            question=question_text,
                            solution=solution_text
                        )
                        solutions.append(solution_text)
                        question.save()
                        
                        if hint_text:
                            hint = PuzzleQuestionHint(
                                question=question,
                                hint=hint_text
                            )
                            hint.save()
            
            solutions.sort()
            encrypted_message = encrypt_message(
                words=solutions,
                message=form.cleaned_data['message']
            )

            daily_challenge.encrypted_message = encrypted_message['ciphertext']
            daily_challenge.nonce = encrypted_message['nonce']
            daily_challenge.salt = encrypted_message['salt']
            daily_challenge.save()

            messages.success(request, "Daily puzzle created successfully!")

            return redirect('daily:solve_daily_puzzle')
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'admin_create_daily.html', {
                'form': form,
                'question_formset': question_formset,
            })

class SolveDailyPuzzleView(View):
    """
    View to handle the puzzle solving process.
    """
    def get(self, request):
        today = datetime.date.today()

        # Fetch the daily challenge for today
        daily_challenge: DailyChallenge = DailyChallenge.objects.filter(daily_date=today).first()

        # Fetch the questions related to the daily challenge
        questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=daily_challenge)

        if daily_challenge:
            # Render the puzzle solving page with the daily challenge
            return render(request, 'solve_daily_puzzle.html', {
                'daily_challenge': daily_challenge,
                'questions': questions,
                'date': today,
            })
        else:
            # Handle the case where there is no daily challenge for today
            return render(request, 'no_daily_challenge.html', {
                'date': today
            })
        

    def post(self, request):
        today = datetime.date.today()

        # Fetch the daily challenge for today
        daily_challenge: DailyChallenge = DailyChallenge.objects.filter(daily_date=today).first()

        if not daily_challenge:
            # Handle the case where there is no daily challenge for today
            return render(request, 'no_daily_challenge.html', {'date': today})

        # Fetch the questions related to the daily challenge
        questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=daily_challenge)

        # Get the user's answers from the request
        user_answers = request.POST.getlist('answers')
        puzzle_solutions = [question.solution for question in questions]
    
        # Check if the user's answers match the puzzle solutions
        if sorted(user_answers) == sorted(puzzle_solutions):
            # Add the solved event to the database
            solved_daily_challenge = PuzzleSolved(
                puzzle=daily_challenge,
                solved_at=datetime.datetime.now(),
                solved_by=request.user
            )
            solved_daily_challenge.save()

            # Decrypt the message using the solutions as the password
            puzzle_solutions.sort()
            decrypted_message: str = decrypt_message(
                ciphertext=daily_challenge.encrypted_message,
                nonce=daily_challenge.nonce,
                salt=daily_challenge.salt,
                password=puzzle_solutions
            )

            messages.success(request, "Congratulations! You've solved the daily puzzle!")
            return render(request, 'solve_daily_puzzle.html', { 
                'daily_challenge': daily_challenge,
                'questions': questions,
                'decrypted_message': decrypted_message,
            })
        else:
            messages.error(request, "Incorrect answers. Please try again.")
            return render(request, 'solve_daily_puzzle.html', {
                'daily_challenge': daily_challenge,
                'questions': questions,
                'date': today,
            })

class DailyLeaderboardView(View):
    """
    View to display the leaderboard for daily challenges.
    """
    def get(self, request):
        # Get the current date
        today = datetime.date.today()

        # Fetch the last 7 daily challenges
        daily_challenges: QuerySet[DailyChallenge] = DailyChallenge.objects.filter(
            daily_date__gte=today - datetime.timedelta(days=7)
        ).order_by('-daily_date')

        # Fetch the count of solved daily challenges for each user in the last 7 days
        leaderboard_data = (
            Profile.objects.filter(
                solved_puzzles__puzzle__in=daily_challenges
            )
            .annotate(
                solved_count=models.Count('solved_puzzles'),
                fastest_solve=models.Min('solved_puzzles__solved_at')
            )
            .order_by('-solved_count', 'fastest_solve')
        )

        # Enhance challenge objects with solve_count data
        enhanced_challenges = []
        for challenge in daily_challenges:
            solve_count = PuzzleSolved.objects.filter(puzzle=challenge).count()
            enhanced_challenges.append({
                'challenge': challenge,
                'solve_count': solve_count,
                'is_today': challenge.daily_date == today
            })

        # Render the leaderboard template
        return render(request, 'daily_leaderboard.html', {
            'leaderboard_data': leaderboard_data,
            'daily_challenges': enhanced_challenges,
            'today': today,
        })

@staff_member_required
def trigger_daily_challenge(request):
    """Admin-only view to manually trigger daily challenge generation"""
    try:
        management.call_command('generate_daily_challenge')
        return JsonResponse({"status": "success", "message": "Daily challenge generated"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})