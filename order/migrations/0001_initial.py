# Generated by Django 2.1.5 on 2019-02-07 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'service_action',
            },
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
                ('required', models.BooleanField()),
            ],
            options={
                'db_table': 'service_attribute',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.AddField(
            model_name='attribute',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Service'),
        ),
        migrations.AddField(
            model_name='action',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Service'),
        ),
    ]
