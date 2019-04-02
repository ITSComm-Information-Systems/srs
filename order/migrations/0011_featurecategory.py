# Generated by Django 2.1.5 on 2019-03-31 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_auto_20190325_0915'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('display_seq_no', models.PositiveIntegerField(blank=True, null=True, unique=True)),
            ],
        ),
    ]
