# Generated by Django 2.2 on 2019-04-04 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20190404_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='action',
        ),
        migrations.RemoveField(
            model_name='item',
            name='umoscpreorderapiv_ptr',
        ),
        migrations.AddField(
            model_name='item',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='service',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
