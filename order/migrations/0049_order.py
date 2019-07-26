# Generated by Django 2.2 on 2019-06-23 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0048_featurecategory_label'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_reference', models.CharField(max_length=20)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('status', models.CharField(max_length=20)),
                ('chartcom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Chartcom')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Service')),
            ],
            options={
                'db_table': 'order',
            },
        ),
    ]
