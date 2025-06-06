import uuid
from django.db import models
from django.core.exceptions import ValidationError

from users.models import Profile

def validate_hint_words(value):
    """Ensure hint is maximum 2 words"""
    if len(value.split()) > 2:
        raise ValidationError('Hint must be a maximum of 2 words.')

class Puzzle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Encrypting fields #
    encrypted_message = models.TextField(null=False)
    nonce = models.TextField(null=False, default='')
    salt = models.TextField(null=False, default='')

    one_time_view = models.BooleanField(default=False) # True if the puzzle can be only be cracked once
    is_solved = models.BooleanField(default=False)
    self_destruct_at = models.DateTimeField(null=True, blank=True) # DateTime when the puzzle will be deleted, if set
    
    created_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name='puzzles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    
class PuzzleQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    puzzle = models.ForeignKey(Puzzle, null=False, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(null=False, blank=False)
    solution = models.TextField(max_length=50, null=False, blank=False)  # Increased from 30 to 50
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class PuzzleSolved(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    puzzle = models.ForeignKey(Puzzle, null=False, on_delete=models.CASCADE, related_name='solved_puzzles')
    solved_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name='solved_puzzles')
    solved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class PuzzleReport(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    puzzle = models.ForeignKey(Puzzle, null=True, on_delete=models.SET_NULL, related_name='reports')
    reported_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name='reported_puzzles')
    report_reason = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
class PuzzleQuestionHint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(PuzzleQuestion, null=False, on_delete=models.CASCADE, related_name='hints')
    hint = models.TextField(max_length=30, null=False, blank=False, validators=[validate_hint_words])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)