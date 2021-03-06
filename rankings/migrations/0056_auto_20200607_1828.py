# Generated by Django 3.0.7 on 2020-06-07 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0055_auto_20200607_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='individualresult',
            name='heat',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='individualresult',
            name='lane',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='individualresult',
            name='reaction_time',
            field=models.DurationField(blank=True, default=None, null=True),
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.Athlete')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.Competition')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.Team')),
            ],
        ),
        migrations.AddField(
            model_name='competition',
            name='participants',
            field=models.ManyToManyField(through='rankings.Participation', to='rankings.Athlete'),
        ),
    ]
