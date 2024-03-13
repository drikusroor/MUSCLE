# Generated by Django 3.2.24 on 2024-02-27 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('theme', '0001_initial'),
        ('experiment', '0022_alter_experiment_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='theme_config',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='theme.themeconfig'),
        ),
    ]