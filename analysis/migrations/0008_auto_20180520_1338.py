# Generated by Django 2.0.1 on 2018-05-20 11:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0007_groupeventsetup'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groupeventsetup',
            old_name='athlete',
            new_name='athletes',
        ),
    ]