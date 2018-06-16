# Generated by Django 2.0.1 on 2018-05-17 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0007_athlete_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelayOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'Individual'), (2, 'Relay segment'), (3, 'Relay complete')], default=0),
        ),
        migrations.AddField(
            model_name='relayorder',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relay', to='rankings.Event'),
        ),
        migrations.AddField(
            model_name='relayorder',
            name='segment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segment', to='rankings.Event'),
        ),
    ]
