# Generated by Django 2.1.5 on 2019-02-08 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_auto_20190208_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='cart',
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
            name='Cart',
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]
