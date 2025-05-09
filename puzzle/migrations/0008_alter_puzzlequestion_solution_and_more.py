# Generated by Django 5.2 on 2025-05-07 14:23

import puzzle.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0007_puzzlequestionhint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzlequestion',
            name='solution',
            field=models.TextField(max_length=50),
        ),
        migrations.AlterField(
            model_name='puzzlequestionhint',
            name='hint',
            field=models.TextField(max_length=30, validators=[puzzle.models.validate_hint_words]),
        ),
    ]
