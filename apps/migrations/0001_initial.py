# Generated by Django 3.2.4 on 2022-02-12 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EstimateView',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('label', models.IntegerField()),
                ('status', models.CharField(max_length=20)),
                ('status_name', models.CharField(max_length=20)),
                ('wo_number_display', models.CharField(max_length=20)),
                ('pre_order_number', models.IntegerField()),
                ('project_display', models.CharField(max_length=200)),
                ('project_manager', models.CharField(max_length=20)),
                ('assigned_engineer', models.CharField(max_length=20)),
                ('assigned_netops', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'um_bom_estimate_search_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=12)),
                ('name', models.CharField(max_length=50)),
                ('class_code', models.CharField(max_length=2)),
                ('subclass_name', models.CharField(max_length=20)),
                ('manufacturer', models.CharField(max_length=50)),
                ('manufacturer_part_number', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
                'db_table': 'um_bom_item_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='LaborGroup',
            fields=[
                ('id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('rate_1', models.CharField(max_length=80)),
                ('rate_2', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'um_bom_labor_group_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PreDefinedNote',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('subject', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'um_bom_predefined_note_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PreOrder',
            fields=[
                ('pre_order_id', models.IntegerField(primary_key=True, serialize=False)),
                ('wo_number_display', models.CharField(max_length=50)),
                ('pre_order_number', models.IntegerField()),
                ('status_name', models.CharField(max_length=50)),
                ('project_display', models.CharField(max_length=50)),
                ('project_code_display', models.CharField(max_length=50)),
                ('add_info_list_value_name_2', models.CharField(max_length=50)),
                ('add_info_list_value_code_2', models.CharField(max_length=50)),
                ('due_date', models.CharField(max_length=50)),
                ('add_info_list_value_name_1', models.CharField(max_length=50)),
                ('add_info_list_value_code_1', models.CharField(max_length=50)),
                ('department_name', models.CharField(max_length=50)),
                ('form_display_contact_name', models.CharField(max_length=50)),
                ('contact_phone_number', models.CharField(max_length=50)),
                ('contact_email_address', models.CharField(max_length=50)),
                ('comment_text', models.CharField(max_length=200)),
                ('add_info_checkbox_1', models.BooleanField(null=True, verbose_name='Draft Comp-D')),
                ('add_info_checkbox_2', models.BooleanField(null=True, verbose_name="Asbuilt Recv'd-D")),
                ('add_info_checkbox_3', models.BooleanField(null=True, verbose_name='Asbuilt Compl-D')),
                ('add_info_checkbox_4', models.BooleanField(null=True)),
                ('add_info_checkbox_5', models.BooleanField(null=True, verbose_name='Asbuilt/Prints-F')),
                ('add_info_checkbox_6', models.BooleanField(null=True, verbose_name='Closeout Compl-F')),
                ('add_info_checkbox_7', models.BooleanField(null=True, verbose_name='Asbuilt/Prints Received-A')),
                ('add_info_checkbox_8', models.BooleanField(null=True, verbose_name='Assignments Complete-A')),
            ],
            options={
                'db_table': 'um_bom_preorder_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectView',
            fields=[
                ('wo_number_display', models.CharField(max_length=14)),
                ('pre_order_number', models.IntegerField()),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(null=True)),
                ('created_by', models.CharField(max_length=32, null=True)),
                ('update_date', models.DateTimeField(null=True)),
                ('updated_by', models.CharField(max_length=32, null=True)),
                ('woid', models.IntegerField()),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Complete'), (2, 'Open'), (3, 'Rework')], null=True)),
                ('percent_completed', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('health', models.PositiveSmallIntegerField(choices=[(1, 'Red'), (2, 'Yellow'), (3, 'Green')], null=True)),
                ('assigned_date', models.DateTimeField(blank=True, null=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('legacy_parent_id', models.CharField(default=0, max_length=32)),
                ('estimate_id', models.IntegerField()),
                ('status_name', models.CharField(max_length=60)),
                ('project_display', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'um_bom_project_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('labor_id', models.IntegerField(primary_key=True, serialize=False)),
                ('labor_code', models.CharField(max_length=20)),
                ('labor_name_display', models.CharField(max_length=80)),
                ('user_name', models.CharField(max_length=80)),
                ('active', models.PositiveSmallIntegerField()),
                ('wo_group_code', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'um_bom_technician_v',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Workorder',
            fields=[
                ('pre_order_id', models.IntegerField(primary_key=True, serialize=False)),
                ('wo_number_display', models.CharField(max_length=20)),
                ('pre_order_number', models.IntegerField()),
                ('project_display', models.CharField(max_length=200)),
                ('status_name', models.CharField(max_length=10)),
                ('comment_text', models.TextField()),
                ('building_number', models.IntegerField(blank=True, null=True)),
                ('building_name', models.CharField(max_length=100)),
                ('multi_count', models.IntegerField()),
                ('estimate_id', models.IntegerField()),
            ],
            options={
                'db_table': 'um_bom_search_v',
                'managed': False,
            },
        ),
    ]
