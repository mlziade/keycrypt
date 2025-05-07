from django import forms

from .models import DailyChallenge

from puzzle.forms import CreatePuzzleForm
from puzzle.models import Puzzle

class CreateDailyPuzzleForm(CreatePuzzleForm):
    difficulty = forms.ChoiceField(
        required=True,
        choices=DailyChallenge.DifficultyChoices.choices,
        label="Difficulty Level",
        help_text="Select the difficulty level for the puzzle."
    )

    daily_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Challenge Date",
        help_text="Select the date for the challenge."
    )

    theme = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter an optional theme'}),
        label="Theme",
        help_text="You can provide an optional theme for the challenge."
    )

    class Meta(CreatePuzzleForm.Meta):
        model = DailyChallenge
        fields = CreatePuzzleForm.Meta.fields + [
            'difficulty',
            'daily_date',
            'theme',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['one_time_view'] = forms.BooleanField(
            widget=forms.HiddenInput(),
            required=False,
            initial=False,
        )
        self.fields['self_destruct_at'] = forms.DateTimeField(
            widget=forms.HiddenInput(),
            required=False,
            initial=None,
        )

        self.fields['message'].widget.attrs['title'] = self.fields['message'].help_text
        self.fields['difficulty'].widget.attrs['title'] = self.fields['difficulty'].help_text
        self.fields['daily_date'].widget.attrs['title'] = self.fields['daily_date'].help_text
        self.fields['theme'].widget.attrs['title'] = self.fields['theme'].help_text