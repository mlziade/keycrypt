from django.db import models
from django.utils import timezone

from puzzle.models import Puzzle

class DailyChallenge(Puzzle):
    """
    DailyChallenges model to represent daily challenges in the database.
    Inherits from the Puzzle model.
    """

    class DifficultyChoices(models.TextChoices):
        EASY = 'easy'
        MEDIUM = 'medium'
        HARD = 'hard'
        EXPERT = 'expert'

    difficulty = models.CharField(
        max_length=20, 
        choices=DifficultyChoices.choices,
        default=DifficultyChoices.EASY
    )

    daily_date = models.DateField(
        default=timezone.now,
        unique=True, 
        verbose_name='Challenge Date'
        )

    theme = models.TextField(
        null=True, 
        blank=True, 
        verbose_name='Challenge Theme'
    )

    def __str__(self):
        return self.daily_date.strftime("%d/%m/%y")