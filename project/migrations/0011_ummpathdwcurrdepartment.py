# Generated by Django 3.2.4 on 2021-10-07 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_umecommmbidcommodityv_umecommmbidcriticaldate_umecommmbidvendorinput_umecommmbidvendorv_umecommmbidw'),
    ]

    operations = [
        migrations.CreateModel(
            name='UmMpathDwCurrDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deptid', models.CharField(max_length=10)),
                ('dept_effdt', models.DateField()),
                ('dept_eff_status', models.CharField(max_length=1)),
                ('dept_descr', models.CharField(max_length=30)),
                ('emplid', models.CharField(max_length=11)),
                ('dept_grp', models.CharField(max_length=20)),
                ('dept_grp_descr', models.CharField(max_length=30)),
                ('dept_grp_vp_area', models.CharField(max_length=20)),
                ('dept_grp_vp_area_descr', models.CharField(max_length=30)),
                ('dept_grp_campus', models.CharField(max_length=20)),
                ('dept_grp_campus_descr', models.CharField(max_length=30)),
                ('dept_bud_seq', models.CharField(blank=True, max_length=20, null=True)),
                ('dept_bud_seq_descr', models.CharField(blank=True, max_length=30, null=True)),
            ],
            options={
                'db_table': 'PINN_CUSTOM"."UM_MPATHDW_CURR_DEPARTMENT',
                'managed': False,
            },
        ),
    ]
