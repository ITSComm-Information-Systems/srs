# Generated by Django 3.2.4 on 2021-10-07 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0148_arcinstance_amount_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arcinstance',
            name='amount_used',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]