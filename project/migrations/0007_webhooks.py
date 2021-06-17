# Generated by Django 3.1.12 on 2021-06-17 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_choice_choicetag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Webhooks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=20, null=True)),
                ('preorder', models.CharField(max_length=50, null=True)),
                ('device_id', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=50, null=True)),
                ('success', models.BooleanField(default=False)),
                ('issue', models.CharField(default='no issue', max_length=50)),
                ('emailed', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('added', models.CharField(max_length=255, null=True)),
                ('skipped', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
