# Generated by Django 2.1.5 on 2019-04-06 17:44

from django.db import migrations, models
import django.db.models.deletion

from rankings.models import Nationality

class Migration(migrations.Migration):
    dependencies = [
        ('rankings', '0020_event_use_points_in_athlete_total'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True, unique=True)),
                ('flag_code', models.CharField(max_length=10, null=True, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='athlete',
            name='nationality',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='rankings.Nationality'),
        ),
    ]
