# Generated by Django 5.1.6 on 2025-03-25 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('softphone', '0003_zoomtoken_alter_category_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZoomAPI',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=20)),
                ('phone_number', models.CharField(max_length=50)),
                ('dept_id', models.CharField(max_length=10, null=True)),
                ('default_address', models.BooleanField()),
                ('last_updated', models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='selectionv',
            options={'managed': False, 'verbose_name': 'Selection'},
        ),
    ]