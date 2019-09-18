# Generated by Django 2.2 on 2019-09-17 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0062_auto_20190916_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='file',
        ),
        migrations.AddField(
            model_name='attachment',
            name='picture',
            field=models.FileField(blank=True, null=True, upload_to='attachments'),
        ),
    ]
