# Generated by Django 3.0.5 on 2020-05-20 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0013_specialresultgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialresultgroup',
            name='special_results',
            field=models.ManyToManyField(blank=True, null=True, to='analysis.SpecialResult'),
        ),
    ]
