# Generated by Django 5.1.6 on 2025-02-15 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_game_active_index_subgame'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='winner',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
