# Generated by Django 2.0.5 on 2018-08-19 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0017_auto_20180616_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='location',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='competition',
            name='name',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
