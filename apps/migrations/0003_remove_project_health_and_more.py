# Generated by Django 4.1.9 on 2023-05-12 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_estimate_engineer_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='health',
        ),
        migrations.RemoveField(
            model_name='project',
            name='percent_completed',
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Complete'), (2, 'Open')], null=True),
        ),
    ]
