# Generated by Django 3.2 on 2021-04-24 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0061_auto_20210423_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relayteam',
            name='competition',
        ),
    ]
