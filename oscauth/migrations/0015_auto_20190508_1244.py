# Generated by Django 2.2 on 2019-05-08 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('oscauth', '0014_grantor'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='grantor',
            unique_together={('grantor_role', 'granted_role')},
        ),
    ]
