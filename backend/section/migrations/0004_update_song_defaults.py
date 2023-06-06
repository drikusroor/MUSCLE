# Generated by Django 3.2.18 on 2023-06-05 10:11

from django.db import migrations, models
import section.models


class Migration(migrations.Migration):

    dependencies = [
        ('section', '0003_song_as_separate_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='filename',
            field=models.FileField(max_length=255, upload_to=section.models.audio_upload_path),
        ),
        migrations.AlterField(
            model_name='song',
            name='artist',
            field=models.CharField(blank=True, db_index=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='song',
            name='name',
            field=models.CharField(blank=True, db_index=True, default='', max_length=128),
        ),
    ]