# Generated by Django 3.2.15 on 2022-11-29 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0011_alter_result_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='access_info',
            field=models.CharField(default='', max_length=512, null=True),
        ),
    ]