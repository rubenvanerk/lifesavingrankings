# Generated by Django 3.0 on 2019-12-10 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0011_analysisgroup_simulation_in_progress'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisgroup',
            name='simulation_date_from',
            field=models.DateField(null=True),
        ),
    ]
