# Generated by Django 2.2 on 2019-04-14 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20190414_1014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='step',
            name='label',
        ),
        migrations.AlterField(
            model_name='step',
            name='name',
            field=models.CharField(max_length=80),
        ),
    ]
