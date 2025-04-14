from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import QuerySet
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from .forms import CreatePuzzleForm, QuestionFormSet
from .models import Puzzle, PuzzleQuestion, PuzzleSolved, PuzzleReport
from .services import encrypt_message

from users.models import Profile

class CreatePuzzleView(View):
    def get(self, request):
        form: CreatePuzzleForm = CreatePuzzleForm()
        question_formset = QuestionFormSet(prefix='questions')
        return render(request, 'create_puzzle.html', {
            'form': form,
            'question_formset': question_formset,
        })

    def post(self, request):
        form = CreatePuzzleForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')

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

                    if question_text and solution_text:
                        question = PuzzleQuestion(
                            puzzle=puzzle,
                            question=question_text,
                            solution=solution_text
                        )
                        solutions.append(solution_text)
                        question.save()
            
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
            puzzle = Puzzle.objects.get(id=puzzle_id)
            questions = PuzzleQuestion.objects.filter(puzzle=puzzle)

            return render(request, 'view_puzzle.html', {
                'puzzle': puzzle,
                'questions': questions,
            })
        except Puzzle.DoesNotExist:
            messages.error(request, "Puzzle not found.")
            return redirect('home')

class SolvePuzzleView(View):
    def get(self, request, puzzle_id):
        try:
            puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
            questions: QuerySet[PuzzleQuestion] = PuzzleQuestion.objects.filter(puzzle=puzzle)

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

            # If the puzzle hasnt been solved yet, set the is_solved field to True IF the user is not the creator
            if not puzzle.is_solved and request.user != puzzle.created_by:
                puzzle.is_solved = True
                puzzle.save()

            # Get the answers from the form
            answers = request.POST.getlist('answers')
            solutions = [question.solution for question in questions]

            # Check if the answers match the solutions
            if sorted(answers) == sorted(solutions):
                # Added the solved event to the database
                solved_puzzle = PuzzleSolved(
                    puzzle=puzzle,
                    solved_by=request.user if request.user.is_authenticated else None
                )
                solved_puzzle.save()
                messages.success(request, "Congratulations! You've solved the puzzle.")
                return redirect('home')
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

def test_question(request, puzzle_id, question_id):
    try:
        puzzle: Puzzle = Puzzle.objects.get(id=puzzle_id)
        question: PuzzleQuestion = PuzzleQuestion.objects.get(id=question_id, puzzle=puzzle)

        if request.method == 'POST':
            answer = request.POST.get('answer')
            if answer == question.solution:
                return JsonResponse({
                    'status': 'success',
                    'message': "Answer submitted."
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