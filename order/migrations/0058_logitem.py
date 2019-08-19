# Generated by Django 2.2 on 2019-08-19 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0057_auto_20190817_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction', models.CharField(max_length=20)),
                ('local_key', models.CharField(blank=True, max_length=20)),
                ('remote_key', models.CharField(blank=True, max_length=20)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('level', models.CharField(blank=True, max_length=20)),
                ('description', models.TextField(blank=True)),
            ],
        ),
    ]
