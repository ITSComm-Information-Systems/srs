# Generated by Django 2.2 on 2019-04-16 22:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_delete_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.Cart')),
            ],
        ),
    ]
