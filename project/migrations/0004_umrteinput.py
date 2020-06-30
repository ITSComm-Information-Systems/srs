# Generated by Django 2.2 on 2020-06-20 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_umrtecurrenttimeassignedv_umrtelaborgroupv_umrteratelevelv_umrteserviceorderv_umrtetechnicianv'),
    ]

    operations = [
        migrations.CreateModel(
            name='UmRteInput',
            fields=[
                ('uniqname', models.CharField(blank=True, max_length=8, null=True)),
                ('wo_labor_id', models.IntegerField()),
                ('wo_tcom_id', models.FloatField()),
                ('full_prord_wo_number', models.CharField(blank=True, max_length=98, null=True)),
                ('labor_id', models.IntegerField()),
                ('labor_code', models.CharField(max_length=9)),
                ('wo_group_labor_group_id', models.BigIntegerField()),
                ('wo_group_code', models.CharField(blank=True, max_length=32, null=True)),
                ('assigned_date', models.DateField(blank=True, null=True)),
                ('complete_date', models.DateField(blank=True, null=True)),
                ('actual_mins_display', models.CharField(blank=True, max_length=10, null=True)),
                ('notes', models.CharField(blank=True, max_length=4000, null=True)),
                ('date_added', models.DateField(blank=True, null=True)),
                ('date_processed', models.DateField(blank=True, null=True)),
                ('messages', models.CharField(blank=True, max_length=2000, null=True)),
                ('request_no', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_INPUT',
                'managed': False,
            },
        ),
    ]