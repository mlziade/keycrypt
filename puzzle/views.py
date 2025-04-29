from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import QuerySet
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils.timezone import now

from .forms import CreatePuzzleForm, CreatePuzzleQuestionsFormSet
from .models import Puzzle, PuzzleQuestion, PuzzleSolved, PuzzleReport, PuzzleQuestionHint
from .services import encrypt_message, decrypt_message

from users.models import Profile

class CreatePuzzleView(View):
    def get(self, request):
        form: CreatePuzzleForm = CreatePuzzleForm()
        question_formset = CreatePuzzleQuestionsFormSet(prefix='questions')
        return render(request, 'create_puzzle.html', {
            'form': form,
            'question_formset': question_formset,
        })

    def post(self, request):
        form = CreatePuzzleForm(request.POST)
        question_formset = CreatePuzzleQuestionsFormSet(request.POST, prefix='questions')

        if form.is_valid() and question_formset.is_valid():
            # Process the puzzle
            puzzle = form.save(commit=False)

            # If the user is authenticated, set the created_by field to their profile
            if request.user.is_authenticated:
                profile: Profile = request.user
                puzzle.created_by = profile                
            puzzle.save()

            if len(question_formset) == 0:
                messages.error(request, "Please add at least one question.")
                return render(request, 'create_puzzle.html', {
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
                            puzzle=puzzle,
                            question=question_text,
                            solution=solution_text
                        )
                        solutions.append(solution_text)
                        question.save()
                        
                        # Save hint if provided
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

            puzzle.encrypted_message = encrypted_message['ciphertext']
            puzzle.nonce = encrypted_message['nonce']
            puzzle.salt = encrypted_message['salt']
            puzzle.save()

            messages.success(request, "Puzzle created successfully!")

            return redirect('puzzle:view_puzzle', puzzle_id=puzzle.id)
        else:
            # If forms are not valid, re-render the page with errors
            messages.error(request, "Please correct the errors below.")
            return render(request, 'create_puzzle.html', {
                'form': form,
                'question_formset': question_formset,
            })

class ViewPuzzleView(View):
    def get(self, request, puzzle_id):
        try:
            puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
            questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=puzzle)
            hints : QuerySet[PuzzleQuestionHint] = PuzzleQuestionHint.objects.filter(question__in=questions)

            if puzzle.one_time_view and puzzle.is_solved:
                messages.error(request, "This puzzle has already been solved and cannot be viewed again.")
                return redirect('home')
            
            if puzzle.self_destruct_at and now() > puzzle.self_destruct_at:
                messages.error(request, "This puzzle has been deleted.")
                return redirect('home')

            return render(request, 'view_puzzle.html', {
                'puzzle': puzzle,
                'questions': questions,
                'hints': hints,
            })
        except Puzzle.DoesNotExist:
            messages.error(request, "Puzzle not found.")
            return redirect('home')

class SolvePuzzleView(View):
    def get(self, request, puzzle_id):
        try:
            puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
            questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=puzzle)

            if puzzle.one_time_view and puzzle.is_solved:
                messages.error(request, "This puzzle has already been solved and cannot be viewed again.")
                return redirect('home')
            
            if puzzle.self_destruct_at and now() > puzzle.self_destruct_at:
                messages.error(request, "This puzzle has been deleted.")
                return redirect('home')

            return render(request, 'solve_puzzle.html', {
                'puzzle': puzzle,
                'questions': questions,
            })
        except Puzzle.DoesNotExist:
            messages.error(request, "Puzzle not found.")
            return redirect('home')
        
    def post(self, request, puzzle_id):
        try:
            puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
            questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=puzzle)

            # Get the answers from the form
            user_answers = request.POST.getlist('answers')
            puzzle_solutions = [question.solution for question in questions]

            # Check if the answers match the solutions
            if sorted(user_answers) == sorted(puzzle_solutions):
                # Added the solved event to the database
                solved_puzzle = PuzzleSolved(
                    puzzle=puzzle,
                    solved_by=request.user if request.user.is_authenticated else None
                )
                solved_puzzle.save()

                # If the puzzle hasnt been solved yet, set the is_solved field to True IF the user is not the creator
                if not puzzle.is_solved and request.user != puzzle.created_by:
                    puzzle.is_solved = True
                    puzzle.save()

                # Decrypt the message using the solutions as the password
                puzzle_solutions.sort()
                decrypted_message: str = decrypt_message(
                    ciphertext=puzzle.encrypted_message,
                    nonce=puzzle.nonce,
                    salt=puzzle.salt,
                    password=puzzle_solutions,
                )

                messages.success(request, "Congratulations! You've solved the puzzle.")
                return render(request, 'solve_puzzle.html', {
                    'puzzle': puzzle,
                    'questions': questions,
                    'decrypted_message': decrypted_message,
                })
            else:
                messages.error(request, "Incorrect answers. Please try again.")
                return render(request, 'solve_puzzle.html', {
                    'puzzle': puzzle,
                    'questions': questions,
                })
        except Puzzle.DoesNotExist:
            messages.error(request, "Puzzle not found.")
            return redirect('home')

class MyPuzzlesView(View):
    @method_decorator(login_required)
    def get(self, request):
        puzzles = Puzzle.objects.filter(created_by=request.user)
        return render(request, 'user_puzzles.html', {
            'puzzles': puzzles,
        })

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def test_question(request, puzzle_id, question_id):
    try:
        puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
        question: PuzzleQuestion = PuzzleQuestion.objects.get(id=question_id, puzzle=puzzle)

        if request.method == 'POST':
            answer = request.POST.get('answer')

            distance = levenshtein_distance(answer, question.solution)

            if answer == question.solution:
                return JsonResponse({
                    'status': 'success',
                    'message': "Answer submitted."
                })
            elif distance <= 3:
                return JsonResponse({
                    'status': 'error',
                    'message': "Close, but not quite right..."
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': "Incorrect answer."
                })
        else:
            return JsonResponse({
                    'status': 'error',
                    'message': "Method not allowed."
                }, status=405)
        
    except (Puzzle.DoesNotExist, PuzzleQuestion.DoesNotExist):
        messages.error(request, "Puzzle or question not found.")
        return redirect('home')

def show_hint(request, puzzle_id, question_id):
    """
    Show hints for a specific question in the puzzle.
    Returns the first hint available for the question.
    """
    try:
        # First verify the puzzle exists and is accessible
        puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
        
        # Check if puzzle should be accessible
        if puzzle.one_time_view and puzzle.is_solved:
            return JsonResponse({
                'status': 'error',
                'message': "This puzzle has already been solved and cannot be viewed."
            }, status=403)
        
        if puzzle.self_destruct_at and now() > puzzle.self_destruct_at:
            return JsonResponse({
                'status': 'error',
                'message': "This puzzle has been deleted."
            }, status=404)
        
        # Get the question, ensuring it belongs to this puzzle
        question: PuzzleQuestion = PuzzleQuestion.objects.get(id=question_id, puzzle=puzzle)
        
        # Use the related_name from the model to get hints directly
        hints = question.hints.all().order_by('id')  # Order by ID to get the first hint

        if hints.exists():
            hint = hints.first().hint
            return JsonResponse({
                'status': 'success',
                'hint': hint,
                'hint_count': hints.count()
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': "No hints available for this question."
            }, status=404)
            
    except Puzzle.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': "Puzzle not found."
        }, status=404)
    except PuzzleQuestion.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': "Question not found for this puzzle."
        }, status=404)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error showing hint: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': "An error occurred while retrieving the hint."
        }, status=500)

def report_puzzle(request, puzzle_id):
    if request.method == 'POST':
        try:
            puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
            report_reason = request.POST.get('report_reason', '').strip()

            # Create a report for the puzzle
            puzzle_report = PuzzleReport(
                puzzle=puzzle,
                reported_by=request.user if request.user.is_authenticated else None,
                report_reason=report_reason
            )
            puzzle_report.save()

            messages.success(request, "Puzzle reported successfully.")
            return redirect('home')
        except Puzzle.DoesNotExist:
            messages.error(request, "Puzzle not found.")
            return redirect('home')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('home')