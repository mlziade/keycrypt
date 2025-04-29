from django import forms
from django.forms import formset_factory
from .models import Puzzle

class CreatePuzzleForm(forms.ModelForm):
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter the message to be encrypted/hidden'}),
        label="Message",
        help_text="Enter the message you want to encrypt and hide."
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

class CreatePuzzleQuestionsForm(forms.Form):
    question = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the question'}),
        label="Question",
    )

    solution = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the answer to the question'}),
        label="Solution",
        help_text="The solution must be a single word."
    )
    
    hint = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter an optional hint (maximum 10 characters)'}),
        label="Hint (Optional)",
        help_text="You can provide an optional hint for this question."
    )

    def clean_solution(self):
        solution = self.cleaned_data.get('solution')
        if ' ' in solution.strip():
            raise forms.ValidationError("The solution must be a single word.")
        return solution
        
    def clean_hint(self):
        hint = self.cleaned_data.get('hint')
        if hint:
            hint = hint.strip()
            if ' ' in hint:
                raise forms.ValidationError("The hint must be a single word.")
            if len(hint) > 10:
                raise forms.ValidationError("The hint must be at most 10 characters long.")
        return hint

CreatePuzzleQuestionsFormSet = formset_factory(CreatePuzzleQuestionsForm, extra=0, max_num=10, min_num=1)