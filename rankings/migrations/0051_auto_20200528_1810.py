# Generated by Django 3.0.5 on 2020-05-28 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0050_medal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medal',
            old_name='gender',
            new_name='rank',
        ),
    ]
