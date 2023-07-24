# Generated by Django 4.1.7 on 2023-07-24 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oscauth', '0001_initial'),
        ('services', '0002_alter_container_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiDesktopNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(default='TBD', max_length=30)),
                ('status', models.CharField(choices=[('A', 'Active'), ('E', 'Ended'), ('P', 'Pending')], default='A', max_length=1)),
                ('account_id', models.CharField(default='TBD', max_length=30)),
                ('created_date', models.DateField(auto_now=True)),
                ('access_internet', models.BooleanField(blank=True, default=False)),
                ('subnet_mask', models.CharField(blank=True, max_length=80)),
                ('ips_protection', models.BooleanField(blank=True, default=False)),
                ('technical_contact', models.CharField(blank=True, max_length=80)),
                ('business_contact', models.CharField(blank=True, max_length=80)),
                ('security_contact', models.CharField(blank=True, max_length=80)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oscauth.ldapgroup')),
            ],
            options={
                'verbose_name': 'MiDesktop Network',
            },
        ),
    ]
