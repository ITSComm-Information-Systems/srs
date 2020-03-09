# Generated by Django 2.2 on 2020-02-12 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UmBillInputApiV',
            fields=[
                ('um_bill_input_id', models.IntegerField(primary_key=True, serialize=False)),
                ('data_source', models.CharField(max_length=50)),
                ('assign_date', models.CharField(max_length=20)),
                ('unique_identifier', models.CharField(max_length=200)),
                ('short_code', models.CharField(max_length=100)),
                ('charge_identifier', models.CharField(max_length=200)),
                ('quantity_vouchered', models.IntegerField()),
                ('invoice_id', models.CharField(max_length=100)),
                ('m_uniqname', models.CharField(max_length=100)),
                ('voucher_comment', models.CharField(max_length=100)),
                ('load_date', models.DateField()),
                ('date_processed', models.DateField(null=True)),
                ('full_input_record', models.CharField(max_length=1000)),
                ('bill_input_file_id', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=13)),
            ],
            options={
                'db_table': 'PS_RATING"."um_bill_input_api_v',
                'managed': False,
            },
        ),
    ]