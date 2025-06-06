# Generated by Django 5.2 on 2025-04-13 15:34

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0003_puzzle_nonce_puzzle_salt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='puzzlequestions',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
