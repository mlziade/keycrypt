from django import forms
from django.forms import formset_factory
from .models import Puzzle, validate_hint_words

class CreatePuzzleForm(forms.ModelForm):
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter the message to be encrypted/hidden (max 280 characters)'}),
        label="Message",
        help_text="Enter the message you want to encrypt and hide (maximum 280 characters)."
    )

    self_destruct_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Self-Destruct At (Optional)",
        help_text="Set an optional date and time for the puzzle to be automatically deleted."
    )

    class Meta:
        model = Puzzle
        fields = [
            'one_time_view',
            'self_destruct_at',
        ]

        widgets = {
            'self_destruct_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'one_time_view': 'Allow only one view?',
        }
        help_texts = {
            'one_time_view': 'If checked, the puzzle can only be successfully viewed/solved once.',
            'self_destruct_at': 'Set an optional date and time for the puzzle to be automatically deleted.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) > 280:
            raise forms.ValidationError("Message cannot exceed 280 characters.")
        return message

class CreatePuzzleQuestionsForm(forms.Form):
    question = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the question'}),
        label="Question",
    )

    solution = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the answer to the question (max 50 characters)'}),
        label="Solution",
        help_text="The solution must be at most 50 characters."
    )
    
    hint = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter an optional hint (max 2 words, 30 characters)'}),
        label="Hint (Optional)",
        help_text="You can provide an optional hint for this question (maximum 2 words, 30 characters)."
    )

    def clean_solution(self):
        solution = self.cleaned_data.get('solution')
        if len(solution) > 50:
            raise forms.ValidationError("The solution must be at most 50 characters long.")
        return solution
        
    def clean_hint(self):
        hint = self.cleaned_data.get('hint')
        if hint:
            hint = hint.strip()
            if len(hint) > 30:
                raise forms.ValidationError("The hint must be at most 30 characters long.")
            
            # Check word count
            if len(hint.split()) > 2:
                raise forms.ValidationError("The hint must be at most 2 words.")
        return hint

CreatePuzzleQuestionsFormSet = formset_factory(CreatePuzzleQuestionsForm, extra=0, max_num=10, min_num=1)

class SolvePuzzleForm(forms.Form):
    def __init__(self, puzzle, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add a field for each question in the puzzle
        questions = puzzle.questions.all()
        for question in questions:
            field_name = f"answer_{question.id}"
            self.fields[field_name] = forms.CharField(
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'form-control me-2',
                    'placeholder': 'Your answer',
                    'id': f"answer-{question.id}"
                }),
                label=""
            )