# Generated by Django 5.2 on 2025-04-08 17:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_doctor_available_time_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='available_time_end',
            field=models.TimeField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='available_time_start',
            field=models.TimeField(default=datetime.date.today),
        ),
    ]
