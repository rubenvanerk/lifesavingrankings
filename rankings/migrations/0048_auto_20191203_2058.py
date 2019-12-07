# Generated by Django 2.1.11 on 2019-12-03 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0047_event_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualResultSplit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DurationField()),
                ('distance', models.IntegerField(default=0)),
                ('individual_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.IndividualResult')),
            ],
            options={
                'ordering': ('distance', 'time'),
            },
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.CharField(max_length=60, unique=True),
        ),
    ]