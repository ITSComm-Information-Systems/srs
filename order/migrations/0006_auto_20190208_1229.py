# Generated by Django 2.1.5 on 2019-02-08 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20190208_1227'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order',
            new_name='Cart',
        ),
        migrations.AlterModelTable(
            name='cart',
            table=None,
        ),
    ]
