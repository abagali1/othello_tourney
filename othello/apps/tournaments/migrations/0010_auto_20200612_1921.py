# Generated by Django 3.0.7 on 2020-06-12 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0009_auto_20200611_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentplayer',
            name='ranking',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=15),
        ),
    ]
