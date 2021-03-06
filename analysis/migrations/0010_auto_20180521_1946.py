# Generated by Django 2.0.5 on 2018-05-21 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0010_auto_20180517_1144'),
        ('analysis', '0009_auto_20180520_1415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupeventsetup',
            name='athletes'
        ),
        migrations.CreateModel(
            name='GroupEvenSetupSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rankings.Athlete')),
            ],
        ),
        migrations.AddField(
            model_name='groupeventsetup',
            name='athletes',
            field=models.ManyToManyField(through='analysis.GroupEvenSetupSegment', to='rankings.Athlete'),
        ),
        migrations.AddField(
            model_name='groupevensetupsegment',
            name='group_event_setup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.GroupEventSetup'),
        ),
    ]
