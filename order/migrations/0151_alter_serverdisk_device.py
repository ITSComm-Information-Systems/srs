# Generated by Django 3.2.4 on 2021-12-09 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0150_auto_20211208_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverdisk',
            name='device',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15)], default=0),
        ),
    ]
