# Generated by Django 3.2.4 on 2022-01-08 12:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('oscauth', '0023_alter_ldapgroup_options'),
        ('project', '0012_umoscacctchangerequest_umoscauthusersapi'),
    ]

    operations = [
        migrations.CreateModel(
            name='Azure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=30)),
                ('billing_contact', models.CharField(max_length=8)),
                ('shortcode', models.CharField(max_length=6)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GCP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=30)),
                ('billing_contact', models.CharField(max_length=8)),
                ('shortcode', models.CharField(max_length=6)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GCPProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.gcp')),
            ],
        ),
        migrations.CreateModel(
            name='AWS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=30)),
                ('billing_contact', models.CharField(max_length=8)),
                ('shortcode', models.CharField(max_length=6)),
                ('requestor', models.CharField(max_length=8)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('data_classification', models.CharField(blank=True, max_length=10, null=True)),
                ('egress_waiver', models.BooleanField()),
                ('security_contact', models.CharField(max_length=30)),
                ('vpn', models.BooleanField()),
                ('non_regulated_data', models.ManyToManyField(blank=True, limit_choices_to={'parent__code': 'NON_REGULATED_SENSITIVE_DATA'}, related_name='aws_nonreg', to='project.Choice')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='oscauth.ldapgroup')),
                ('regulated_data', models.ManyToManyField(blank=True, limit_choices_to={'parent__code': 'REGULATED_SENSITIVE_DATA'}, related_name='aws_regulated', to='project.Choice')),
                ('version', models.ForeignKey(limit_choices_to={'parent__code': 'AWS_VERSION'}, on_delete=django.db.models.deletion.CASCADE, to='project.choice')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
