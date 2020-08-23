# Generated by Django 2.2 on 2020-07-22 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0110_auto_20200715_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='external_reference_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='backupdomain',
            name='size',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]