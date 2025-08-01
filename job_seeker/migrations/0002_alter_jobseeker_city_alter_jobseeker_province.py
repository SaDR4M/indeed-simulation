# Generated by Django 5.1.5 on 2025-02-23 08:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_seeker', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobseeker',
            name='city',
            field=models.ForeignKey(default=301, on_delete=django.db.models.deletion.CASCADE, related_name='city_jobseekers', to='location.cities'),
        ),
        migrations.AlterField(
            model_name='jobseeker',
            name='province',
            field=models.ForeignKey(default=8, on_delete=django.db.models.deletion.CASCADE, related_name='state_jobseekers', to='location.provinces'),
        ),
    ]
