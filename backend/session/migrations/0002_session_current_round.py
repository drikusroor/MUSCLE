# Generated by Django 3.2.16 on 2023-02-06 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='current_round',
            field=models.IntegerField(default=0),
        ),
    ]
