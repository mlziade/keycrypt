import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import QuerySet
from django.db import models
from django.views import View
from django.core import management
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.core.paginator import Paginator
from django.utils import timezone

from .models import DailyChallenge
from .forms import CreateDailyPuzzleForm

from puzzle.models import PuzzleQuestion, PuzzleQuestionHint, PuzzleSolved
from puzzle.forms import CreatePuzzleQuestionsFormSet, SolvePuzzleForm
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

class SolveCurrentDailyPuzzleView(View):
    """
    View to handle the puzzle solving process.
    """
    def get(self, request):
        today = datetime.date.today()

        # Fetch the daily challenge for today
        daily_challenge: DailyChallenge = DailyChallenge.objects.filter(daily_date=today).first()

        if daily_challenge:
            # Fetch the questions related to the daily challenge
            questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=daily_challenge)
            
            # Create the form for the daily challenge
            form = SolvePuzzleForm(puzzle=daily_challenge)

            # Render the puzzle solving page with the daily challenge
            return render(request, 'solve_daily_puzzle.html', {
                'daily_challenge': daily_challenge,
                'questions': questions,
                'date': today,
                'form': form,
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
        
        # Create and validate the form
        form = SolvePuzzleForm(puzzle=daily_challenge, data=request.POST)
        
        if form.is_valid():
            all_correct = True
            original_solutions = []
            
            # Check each answer against its specific question (case-insensitive)
            for question in questions:
                field_name = f"answer_{question.id}"
                user_answer = form.cleaned_data[field_name]
                
                # Case-insensitive comparison for validation
                if user_answer.lower() != question.solution.lower():
                    all_correct = False
                    break
                
                # Keep original case for decryption
                original_solutions.append(question.solution)
                
            if all_correct:
                # Add the solved event to the database
                solved_daily_challenge = PuzzleSolved(
                    puzzle=daily_challenge,
                    solved_at=datetime.datetime.now(),
                    solved_by=request.user if request.user.is_authenticated else None
                )
                solved_daily_challenge.save()

                # Decrypt the message using the original case solutions
                original_solutions.sort()
                decrypted_message = decrypt_message(
                    ciphertext=daily_challenge.encrypted_message,
                    nonce=daily_challenge.nonce,
                    salt=daily_challenge.salt,
                    password=original_solutions
                )

                messages.success(request, "Congratulations! You've solved the daily puzzle!")
                return render(request, 'solve_daily_puzzle.html', { 
                    'daily_challenge': daily_challenge,
                    'questions': questions,
                    'decrypted_message': decrypted_message,
                    'form': form,
                })
            else:
                messages.error(request, "Incorrect answers. Please try again.")
        else:
            messages.error(request, "Please provide all answers.")
            
        return render(request, 'solve_daily_puzzle.html', {
            'daily_challenge': daily_challenge,
            'questions': questions,
            'date': today,
            'form': form,
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
        
        # Only count puzzles solved on the same day they were published
        leaderboard_data = (
            Profile.objects.filter(
                solved_puzzles__puzzle__in=daily_challenges,
                solved_puzzles__solved_at__date=models.F('solved_puzzles__puzzle__dailychallenge__daily_date')
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
    
    today = datetime.date.today()
    
    # Check if a daily challenge already exists for today
    puzzle_exists_before = DailyChallenge.objects.filter(daily_date=today).exists()
    
    try:
        # Run the command
        call_command('create_daily_llm_challenge')
        
        # Check if a daily challenge exists now
        puzzle_exists_after = DailyChallenge.objects.filter(daily_date=today).exists()
        
        if puzzle_exists_before:
            return JsonResponse({
                "status": "error",
                "message": f"Daily challenge for {today} already exists."
            })
        elif puzzle_exists_after:
            return JsonResponse({
                "status": "success",
                "message": f"Daily challenge for {today} created successfully."
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Failed to create daily challenge. Check server logs for details."
            })
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "message": f"Failed to generate daily challenge: {str(e)}"
        })

class ListPreviousDailyPuzzlesView(View):
    """
    View to display paginated list of previous daily challenges.
    """
    def get(self, request):
        today = datetime.date.today()
        
        # Get all previous daily challenges (not today's)
        previous_challenges = DailyChallenge.objects.filter(
            daily_date__lt=today
        ).order_by('-daily_date')
        
        # Pagination
        items_per_page = request.GET.get('per_page', 10)
        try:
            items_per_page = int(items_per_page)
            if items_per_page not in [5, 10, 25, 50]:
                items_per_page = 10
        except (ValueError, TypeError):
            items_per_page = 10
            
        paginator = Paginator(previous_challenges, items_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add solved status for current user
        if request.user.is_authenticated:
            solved_puzzle_ids = set(
                PuzzleSolved.objects.filter(
                    puzzle__in=page_obj.object_list,
                    solved_by=request.user
                ).values_list('puzzle_id', flat=True)
            )
        else:
            solved_puzzle_ids = set()
            
        # Enhance challenges with solve status and counts
        enhanced_challenges = []
        for challenge in page_obj.object_list:
            solve_count = PuzzleSolved.objects.filter(puzzle=challenge).count()
            enhanced_challenges.append({
                'challenge': challenge,
                'solve_count': solve_count,
                'is_solved': challenge.id in solved_puzzle_ids
            })
        
        return render(request, 'list_previous_daily_puzzles.html', {
            'page_obj': page_obj,
            'enhanced_challenges': enhanced_challenges,
            'items_per_page': items_per_page,
            'today': today,
        })

class SolvePreviousDailyPuzzleView(View):
    """
    View to handle solving previous daily puzzles.
    """
    def get(self, request, puzzle_id):
        daily_challenge = get_object_or_404(DailyChallenge, id=puzzle_id)
        
        # Check if this puzzle is from today (should use current daily puzzle view)
        if daily_challenge.daily_date == datetime.date.today():
            return redirect('daily:solve_daily_puzzle')
        
        # Fetch the questions related to the daily challenge
        questions = PuzzleQuestion.objects.filter(puzzle=daily_challenge)
        
        # Create the form for the daily challenge
        form = SolvePuzzleForm(puzzle=daily_challenge)
        
        # Check if user already solved this puzzle
        user_solved = False
        if request.user.is_authenticated:
            user_solved = PuzzleSolved.objects.filter(
                puzzle=daily_challenge,
                solved_by=request.user
            ).exists()
        
        return render(request, 'solve_previous_daily_puzzle.html', {
            'daily_challenge': daily_challenge,
            'questions': questions,
            'form': form,
            'user_solved': user_solved,
        })
    
    def post(self, request, puzzle_id):
        daily_challenge = get_object_or_404(DailyChallenge, id=puzzle_id)
        
        # Check if this puzzle is from today
        if daily_challenge.daily_date == datetime.date.today():
            return redirect('daily:solve_daily_puzzle')
        
        # Check if user already solved this puzzle
        if request.user.is_authenticated:
            already_solved = PuzzleSolved.objects.filter(
                puzzle=daily_challenge,
                solved_by=request.user
            ).exists()
            
            if already_solved:
                messages.info(request, "You have already solved this puzzle!")
                return redirect('daily:solve_previous_puzzle', puzzle_id=puzzle_id)
        
        # Fetch the questions related to the daily challenge
        questions = PuzzleQuestion.objects.filter(puzzle=daily_challenge)
        
        # Create and validate the form
        form = SolvePuzzleForm(puzzle=daily_challenge, data=request.POST)
        
        if form.is_valid():
            all_correct = True
            original_solutions = []
            
            # Check each answer against its specific question (case-insensitive)
            for question in questions:
                field_name = f"answer_{question.id}"
                user_answer = form.cleaned_data[field_name]
                
                # Case-insensitive comparison for validation
                if user_answer.lower() != question.solution.lower():
                    all_correct = False
                    break
                
                # Keep original case for decryption
                original_solutions.append(question.solution)
                
            if all_correct:
                # Add the solved event to the database
                solved_daily_challenge = PuzzleSolved(
                    puzzle=daily_challenge,
                    solved_at=datetime.datetime.now(),
                    solved_by=request.user if request.user.is_authenticated else None
                )
                solved_daily_challenge.save()

                # Decrypt the message using the original case solutions
                original_solutions.sort()
                decrypted_message = decrypt_message(
                    ciphertext=daily_challenge.encrypted_message,
                    nonce=daily_challenge.nonce,
                    salt=daily_challenge.salt,
                    password=original_solutions
                )

                messages.success(request, "Congratulations! You've solved this daily puzzle!")
                return render(request, 'solve_previous_daily_puzzle.html', { 
                    'daily_challenge': daily_challenge,
                    'questions': questions,
                    'decrypted_message': decrypted_message,
                    'form': form,
                    'user_solved': True,
                })
            else:
                messages.error(request, "Incorrect answers. Please try again.")
        else:
            messages.error(request, "Please provide all answers.")
            
        return render(request, 'solve_previous_daily_puzzle.html', {
            'daily_challenge': daily_challenge,
            'questions': questions,
            'form': form,
            'user_solved': False,
        })

class ViewDailySolutionView(View):
    """
    View to display the solution for a daily puzzle.
    """
    def get(self, request, puzzle_id):
        daily_challenge = get_object_or_404(DailyChallenge, id=puzzle_id)
        
        # Check if this is today's puzzle and not yet solved by user
        today = datetime.date.today()
        if daily_challenge.daily_date == today:
            if request.user.is_authenticated:
                user_solved = PuzzleSolved.objects.filter(
                    puzzle=daily_challenge,
                    solved_by=request.user
                ).exists()
                if not user_solved:
                    messages.warning(request, "You can only view the solution after solving today's puzzle!")
                    return redirect('daily:solve_daily_puzzle')
        
        # Fetch the questions and solutions
        questions = PuzzleQuestion.objects.filter(puzzle=daily_challenge)
        
        # Decrypt the message using the solutions
        solutions = [q.solution for q in questions]
        solutions.sort()
        
        decrypted_message = decrypt_message(
            ciphertext=daily_challenge.encrypted_message,
            nonce=daily_challenge.nonce,
            salt=daily_challenge.salt,
            password=solutions
        )
        
        return render(request, 'view_daily_solution.html', {
            'daily_challenge': daily_challenge,
            'questions': questions,
            'decrypted_message': decrypted_message,
        })