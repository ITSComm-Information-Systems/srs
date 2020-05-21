# Generated by Django 2.2.1 on 2020-05-21 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_umbillinputapiv'),
    ]

    operations = [
        migrations.CreateModel(
            name='UmRteCurrentTimeAssignedV',
            fields=[
                ('wo_labor_id', models.IntegerField(primary_key=True, serialize=False)),
                ('wo_tcom_id', models.FloatField()),
                ('category_code', models.CharField(max_length=1)),
                ('project_type_code', models.CharField(blank=True, max_length=3, null=True)),
                ('project_number', models.FloatField(blank=True, null=True)),
                ('project_name', models.CharField(blank=True, max_length=50, null=True)),
                ('work_order_display', models.CharField(blank=True, max_length=98, null=True)),
                ('pre_order_number', models.BigIntegerField(blank=True, null=True)),
                ('pre_order_issue', models.BigIntegerField(blank=True, null=True)),
                ('wo_type_code', models.CharField(blank=True, max_length=2, null=True)),
                ('wo_number', models.IntegerField(blank=True, null=True)),
                ('wo_issue', models.IntegerField(blank=True, null=True)),
                ('status_name', models.CharField(blank=True, max_length=60, null=True)),
                ('work_status_name', models.CharField(blank=True, max_length=71, null=True)),
                ('assigned_labor_code', models.CharField(blank=True, max_length=9, null=True)),
                ('is_occ_billed', models.FloatField(blank=True, null=True)),
                ('billed', models.CharField(blank=True, max_length=3, null=True)),
                ('labor_code', models.CharField(blank=True, max_length=9, null=True)),
                ('labor_name_display', models.CharField(blank=True, max_length=104, null=True)),
                ('skill_code', models.CharField(blank=True, max_length=3, null=True)),
                ('skill_name', models.CharField(blank=True, max_length=25, null=True)),
                ('labor_cost_name', models.CharField(blank=True, max_length=60, null=True)),
                ('rate_used', models.DecimalField(decimal_places=4, max_digits=19)),
                ('assigned_date', models.DateField(blank=True, null=True)),
                ('actual_mins', models.BigIntegerField()),
                ('actual_mins_display', models.CharField(blank=True, max_length=10, null=True)),
                ('assn_wo_group_code', models.CharField(blank=True, max_length=32, null=True)),
                ('assn_wo_group_name', models.CharField(blank=True, max_length=64, null=True)),
                ('comment_text', models.CharField(blank=True, max_length=4000, null=True)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_CURRENT_TIME_ASSIGNED_V',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UmRteLaborGroupV',
            fields=[
                ('wo_group_labor_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('wo_group_labor_group_id', models.BigIntegerField()),
                ('wo_group_code', models.CharField(blank=True, max_length=32, null=True)),
                ('wo_group_name', models.CharField(blank=True, max_length=64, null=True)),
                ('labor_id', models.IntegerField()),
                ('wo_group_labor_code', models.CharField(max_length=9)),
                ('labor_name_display', models.CharField(blank=True, max_length=104, null=True)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_LABOR_GROUP_V',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UmRteRateLevelV',
            fields=[
                ('labor_rate_level_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('labor_rate_level_name', models.CharField(max_length=60)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_RATE_LEVEL_V',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UmRteServiceOrderV',
            fields=[
                ('wo_tcom_id', models.FloatField(primary_key=True, serialize=False)),
                ('full_prord_wo_number', models.CharField(blank=True, max_length=98, null=True)),
                ('pre_order_number', models.BigIntegerField(blank=True, null=True)),
                ('pre_order_issue', models.BigIntegerField(blank=True, null=True)),
                ('wo_type_code', models.CharField(blank=True, max_length=2, null=True)),
                ('wo_number', models.IntegerField(blank=True, null=True)),
                ('wo_issue', models.IntegerField(blank=True, null=True)),
                ('status_name', models.CharField(blank=True, max_length=60, null=True)),
                ('category_code', models.CharField(max_length=1)),
                ('assigned_labor_code', models.CharField(blank=True, max_length=9, null=True)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_SERVICE_ORDER_V',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UmRteTechnicianV',
            fields=[
                ('labor_id', models.IntegerField(primary_key=True, serialize=False)),
                ('labor_code', models.CharField(max_length=9)),
                ('labor_name_display', models.CharField(blank=True, max_length=4000, null=True)),
                ('labor_name_display2', models.CharField(blank=True, max_length=4000, null=True)),
                ('uniqname', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_RTE_TECHNICIAN_V',
                'managed': False,
            },
        ),
    ]
