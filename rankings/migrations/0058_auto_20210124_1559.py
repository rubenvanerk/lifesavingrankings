# Generated by Django 3.0.7 on 2021-01-24 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0057_points_to_integer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='competition',
            old_name='location',
            new_name='city',
        ),
        migrations.AddField(
            model_name='competition',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rankings.Nationality'),
        ),
        migrations.AddField(
            model_name='competition',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
