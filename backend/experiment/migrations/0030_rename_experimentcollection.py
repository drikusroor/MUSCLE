# Generated by Django 3.2.25 on 2024-04-08 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0029_experimentseriesgroup_finished'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExperimentSeries',
            new_name='ExperimentCollection',
        ),
        migrations.RenameModel(
            old_name='ExperimentSeriesGroup',
            new_name='ExperimentCollectionGroup',
        ),
    ]