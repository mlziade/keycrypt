# Generated by Django 5.2 on 2025-04-17 04:00

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0006_puzzlereport'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuzzleQuestionHint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hint', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hints', to='puzzle.puzzlequestion')),
            ],
        ),
    ]
