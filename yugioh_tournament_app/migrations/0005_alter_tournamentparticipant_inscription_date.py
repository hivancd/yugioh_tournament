# Generated by Django 5.0.1 on 2024-02-07 03:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yugioh_tournament_app', '0004_remove_duel_loser_duel_player1_duel_player2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentparticipant',
            name='inscription_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 6, 22, 12, 44, 326825)),
        ),
    ]
