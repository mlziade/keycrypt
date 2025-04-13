import uuid
from django.db import models

from users.models import Profile

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
    
class PuzzleQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    puzzle = models.ForeignKey(Puzzle, null=False, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(null=False, blank=False)
    solution = models.TextField(max_length=30, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)