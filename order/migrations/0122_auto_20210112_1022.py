# Generated by Django 3.1.2 on 2021-01-12 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0121_remove_server_disk_space'),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('legacy_data', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='server',
            name='cpu',
            field=models.IntegerField(verbose_name='CPU'),
        ),
        migrations.AlterField(
            model_name='server',
            name='ram',
            field=models.IntegerField(verbose_name='RAM'),
        ),
    ]