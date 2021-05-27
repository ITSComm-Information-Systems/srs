# Generated by Django 3.1.2 on 2020-12-18 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0119_auto_20201217_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='in_service',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='ServerDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('size', models.IntegerField()),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disks', to='order.server')),
            ],
        ),
        migrations.CreateModel(
            name='ServerData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=5)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='order.server')),
            ],
        ),
    ]
