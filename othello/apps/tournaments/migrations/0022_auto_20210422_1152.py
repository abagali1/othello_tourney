# Generated by Django 3.1.7 on 2021-04-22 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0021_tournament_runoff_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentplayer',
            name='ranking',
            field=models.FloatField(default=0),
        ),
    ]
