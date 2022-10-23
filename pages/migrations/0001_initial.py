# Generated by Django 3.2.4 on 2022-09-14 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('permalink', models.CharField(max_length=12, unique=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('bodytext', models.TextField()),
                ('display_seq_no', models.PositiveIntegerField(blank=True, null=True, unique=True)),
            ],
            options={
                'ordering': ('display_seq_no', 'title'),
            },
        ),
    ]
