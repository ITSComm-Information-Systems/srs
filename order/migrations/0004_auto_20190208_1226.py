# Generated by Django 2.1.5 on 2019-02-08 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20190208_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='order',
        ),
        migrations.RemoveField(
            model_name='item',
            name='service',
        ),
        migrations.RemoveField(
            model_name='item',
            name='service_action',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]
