# Generated by Django 3.0.7 on 2020-10-26 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0024_auto_20201026_0259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='name',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
