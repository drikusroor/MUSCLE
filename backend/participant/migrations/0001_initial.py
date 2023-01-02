# Generated by Django 3.2.16 on 2023-01-02 14:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_hash', models.CharField(default=uuid.uuid4, max_length=64, unique=True)),
                ('country_code', models.CharField(default='', max_length=3)),
                ('access_info', models.CharField(default='', max_length=512, null=True)),
            ],
        ),
    ]
