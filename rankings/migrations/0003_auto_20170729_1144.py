# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 09:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0002_specialresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specialresult',
            name='event',
        ),
        migrations.DeleteModel(
            name='SpecialResult',
        ),
    ]
