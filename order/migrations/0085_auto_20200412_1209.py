# Generated by Django 2.2 on 2020-04-12 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0084_auto_20200311_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagehost',
            name='storage_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosts', to='order.StorageInstance'),
        ),
        migrations.AlterField(
            model_name='storageinstance',
            name='ad_group',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='storageinstance',
            name='deptid',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
