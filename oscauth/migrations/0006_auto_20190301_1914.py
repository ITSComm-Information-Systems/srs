# Generated by Django 2.1.5 on 2019-03-02 00:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oscauth', '0005_auto_20190226_1734'),
    ]

    operations = [
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
            name='RolePrivRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('inactivation_date', models.DateTimeField(blank=True, null=True, verbose_name='Date Inactivated')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('created_by', models.CharField(default='Will be autogenerated', max_length=150)),
                ('last_update_date', models.DateTimeField(auto_now=True, verbose_name='Last Date Updated')),
                ('last_updated_by', models.CharField(default='Will be autogenerated', max_length=150)),
                ('privilege', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oscauth.Privilege')),
                ('restriction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oscauth.Restriction')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='oscauth.Role')),
            ],
            options={
                'db_table': 'oscauth_role_priv_restriction',
            },
        ),
        migrations.DeleteModel(
            name='OscAuthUser',
        ),
    ]
