# Generated by Django 2.2 on 2020-06-22 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0105_auto_20200620_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupnode',
            name='time',
            field=models.IntegerField(),
        ),
    ]
