from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import CreatePuzzleForm, QuestionFormSet
from .models import Puzzle, PuzzleQuestions
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

            solutions: list[str] = []

            # Process the questions formset
            for question_form in question_formset:
                if question_form.cleaned_data:
                    question_text = question_form.cleaned_data.get('question')
                    solution_text = question_form.cleaned_data.get('solution')

                    if question_text and solution_text:
                        question = PuzzleQuestions(
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

            return redirect('home')
        else:
            # If forms are not valid, re-render the page with errors
            messages.error(request, "Please correct the errors below.")
            return render(request, 'create_puzzle.html', {
                'form': form,
                'question_formset': question_formset,
            })
