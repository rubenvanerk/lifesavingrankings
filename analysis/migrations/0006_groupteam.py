# Generated by Django 2.0.1 on 2018-05-20 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0010_auto_20180517_1144'),
        ('analysis', '0005_auto_20180114_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.AnalysisGroup')),
                ('athletes', models.ManyToManyField(to='rankings.Athlete')),
            ],
        ),
    ]
