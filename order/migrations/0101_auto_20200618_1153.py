# Generated by Django 2.2 on 2020-06-18 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0100_auto_20200617_1727'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arcinstance',
            old_name='globus_ha',
            new_name='globus_phi',
        ),
    ]