# Generated by Django 3.0.5 on 2020-06-07 10:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0052_athlete_alias_of'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='alias_of',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='rankings.Athlete'),
        ),
    ]
