# Generated by Django 5.0 on 2024-07-23 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_server_production_alter_server_backup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='legacy_data',
        ),
        migrations.AddField(
            model_name='server',
            name='last_updated',
            field=models.DateTimeField(null=True),
        ),
    ]