# Generated by Django 5.0.1 on 2024-03-02 15:53

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yugioh_tournament_app', '0003_rename_user_id_player_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tournamentparticipant',
            name='inscription_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 2, 10, 53, 46, 197414)),
        ),
    ]