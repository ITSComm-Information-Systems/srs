# Generated by Django 4.1.7 on 2023-07-24 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_midesktopnetwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='midesktopnetwork',
            name='purpose',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
