# Generated by Django 3.2.12 on 2022-06-17 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0008_auto_20220517_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]