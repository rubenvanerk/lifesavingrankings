# Generated by Django 3.0.7 on 2021-04-07 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0059_auto_20210406_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='slug',
            field=models.SlugField(max_length=80, null=True),
        ),
    ]
