# Generated by Django 2.1.5 on 2019-04-20 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rankings', '0023_individualresult_original_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='nationalities',
            field=models.ManyToManyField(related_name='nationalities', to='rankings.Nationality'),
        ),
        migrations.AddField(
            model_name='nationality',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='rankings.Nationality'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='nationality',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nationality', to='rankings.Nationality'),
        ),
    ]
