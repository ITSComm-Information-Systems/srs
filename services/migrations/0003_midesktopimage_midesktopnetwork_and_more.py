# Generated by Django 4.1.7 on 2023-08-10 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oscauth', '0001_initial'),
        ('services', '0002_alter_container_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiDesktopImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Active'), ('E', 'Ended'), ('P', 'Pending')], default='A', max_length=1)),
                ('account_id', models.CharField(default='TBD', max_length=30)),
                ('created_date', models.DateField(auto_now=True)),
                ('instance_name', models.CharField(default='TBD', max_length=30, verbose_name='Image Name')),
                ('cpu', models.CharField(max_length=4)),
                ('memory', models.CharField(max_length=4)),
                ('gpu', models.BooleanField(blank=True, null=True)),
                ('total_image_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('pool_id', models.IntegerField()),
                ('network_id', models.IntegerField()),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oscauth.ldapgroup')),
            ],
            options={
                'verbose_name': 'MiDesktop Image',
            },
        ),
        migrations.CreateModel(
            name='MiDesktopNetwork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(default='TBD', max_length=30)),
                ('status', models.CharField(choices=[('A', 'Active'), ('E', 'Ended'), ('P', 'Pending')], default='A', max_length=1)),
                ('account_id', models.CharField(default='TBD', max_length=30)),
                ('created_date', models.DateField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=80)),
                ('size', models.CharField(blank=True, max_length=80)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oscauth.ldapgroup')),
            ],
            options={
                'verbose_name': 'MiDesktop Network',
            },
        ),
        migrations.CreateModel(
            name='MiDesktopInstantClonePool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Active'), ('E', 'Ended'), ('P', 'Pending')], default='A', max_length=1)),
                ('account_id', models.CharField(default='TBD', max_length=30)),
                ('created_date', models.DateField(auto_now=True)),
                ('shortcode', models.CharField(max_length=6)),
                ('instance_name', models.CharField(default='TBD', max_length=30, verbose_name='Pool Name')),
                ('pool_quantity', models.IntegerField()),
                ('pool_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('shared_network', models.BooleanField(default=True)),
                ('image', models.ManyToManyField(to='services.midesktopimage')),
                ('network', models.ManyToManyField(null=True, to='services.midesktopnetwork')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oscauth.ldapgroup')),
            ],
            options={
                'verbose_name': 'MiDesktop Instant Clone Pool',
            },
        ),
        migrations.CreateModel(
            name='ImageDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('size', models.IntegerField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='storage', to='services.midesktopimage')),
            ],
        ),
    ]
