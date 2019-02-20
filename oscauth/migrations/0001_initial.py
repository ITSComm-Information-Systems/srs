# Generated by Django 2.1.5 on 2019-02-20 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_seq_no', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('privilege', models.CharField(max_length=30, unique=True)),
                ('privilege_description', models.CharField(max_length=1000)),
                ('active', models.BooleanField(default=True)),
                ('inactivation_date', models.DateTimeField(blank=True, null=True, verbose_name='Date Inactivated')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.CharField(default='Will be autogenerated', max_length=150)),
                ('last_update_date', models.DateTimeField(auto_now=True, verbose_name='Last Date Updated')),
                ('last_updated_by', models.CharField(default='Will be autogenerated', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_seq_no', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('restriction_type', models.CharField(max_length=10)),
                ('restriction', models.CharField(max_length=30, unique=True)),
                ('restriction_description', models.CharField(max_length=1000)),
                ('active', models.BooleanField(default=True)),
                ('inactivation_date', models.DateTimeField(blank=True, null=True, verbose_name='Date Inactivated')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.CharField(default='Will be autogenerated', max_length=150)),
                ('last_update_date', models.DateTimeField(auto_now=True, verbose_name='Last Date Updated')),
                ('last_updated_by', models.CharField(default='Will be autogenerated', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_seq_no', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('role', models.CharField(max_length=30, unique=True)),
                ('role_description', models.CharField(max_length=1000)),
                ('grantable_by_dept', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('inactivation_date', models.DateTimeField(blank=True, null=True, verbose_name='Date Inactivated')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.CharField(default='Will be autogenerated', max_length=150)),
                ('last_update_date', models.DateTimeField(auto_now=True, verbose_name='Last Date Updated')),
                ('last_updated_by', models.CharField(default='Will be autogenerated', max_length=150)),
            ],
        ),
    ]
