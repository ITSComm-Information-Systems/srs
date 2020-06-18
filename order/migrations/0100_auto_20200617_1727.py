# Generated by Django 2.2 on 2020-06-17 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0099_archost_arcinstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='arcinstance',
            name='thunder_x',
            field=models.BooleanField(default=False, verbose_name='ThunderX'),
        ),
        migrations.AlterField(
            model_name='storageinstance',
            name='owner_bak',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.StorageOwner'),
        ),
        migrations.AlterField(
            model_name='storageinstance',
            name='owner_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
