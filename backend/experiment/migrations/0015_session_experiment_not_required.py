# Generated by Django 3.2.16 on 2022-12-13 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0014_result_question_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='experiment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='experiment.experiment'),
        ),
    ]
