# Generated by Django 2.1.5 on 2019-04-20 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0022_competition_imported_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualresult',
            name='original_line',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]
