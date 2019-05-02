# Generated by Django 2.1.5 on 2019-05-02 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0030_mergerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='first_name',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='last_name',
            field=models.CharField(default=None, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='nationalities',
            field=models.ManyToManyField(default=None, related_name='nationalities', to='rankings.Nationality'),
        ),
    ]
