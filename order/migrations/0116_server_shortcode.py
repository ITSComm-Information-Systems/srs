# Generated by Django 3.1.2 on 2020-12-17 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0115_server_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='shortcode',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]