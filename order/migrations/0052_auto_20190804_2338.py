# Generated by Django 2.2 on 2019-08-05 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0051_auto_20190623_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='display_condition',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='element',
            name='label',
            field=models.TextField(),
        ),
    ]
