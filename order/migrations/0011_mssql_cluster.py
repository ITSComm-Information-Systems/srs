import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import project.models


def add_windows_2025_choice(apps, schema_editor):
    Choice = apps.get_model('project', 'Choice')
    windows_2022 = Choice.objects.filter(code='Windows2022managed').first()
    if not windows_2022 or not windows_2022.parent_id:
        return
    parent = windows_2022.parent
    choice, created = Choice.objects.get_or_create(
        code='Windows2025managed',
        defaults={
            'active': True,
            'sequence': (Choice.objects.filter(parent=parent).order_by('-sequence').values_list('sequence', flat=True).first() or 0) + 1,
            'parent': parent,
            'label': 'Windows Server 2025 - Managed',
        },
    )
    if not created and not choice.active:
        choice.active = True
        choice.save(update_fields=['active'])


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_arcinstance_college_trigger'),
        ('project', '0005_menuitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='cluster_instance_type',
            field=models.CharField(
                blank=True,
                choices=[('d', 'Database'), ('a', 'SSAS')],
                max_length=1,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name='MSSQLCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('environment', models.CharField(choices=[('t', 'Test'), ('n', 'Non-production'), ('p', 'Production')], max_length=1)),
                ('instance_type', models.CharField(choices=[('d', 'Database'), ('a', 'SSAS')], max_length=1)),
                ('sequence', models.CharField(max_length=2)),
                ('application', models.CharField(max_length=100)),
                ('vm_cluster', models.CharField(default='mssqlcluster', max_length=100)),
                ('cpu', models.PositiveIntegerField()),
                ('memory', models.PositiveIntegerField(help_text='Memory in GB; no SRS approval limit.')),
                ('windows_version', models.CharField(choices=[('2022', 'Windows Server 2022'), ('2025', 'Windows Server 2025')], max_length=4)),
                ('shortcode', project.models.ShortCodeField()),
                ('additional_details', models.TextField(blank=True)),
                ('support_email', models.EmailField(default='its.mssqldba@umich.edu', max_length=254)),
                ('support_phone', models.CharField(default='734-822-7754', max_length=30)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('cluster_ticket_id', models.PositiveIntegerField(blank=True, null=True)),
                ('primary_ticket_id', models.PositiveIntegerField(blank=True, null=True)),
                ('secondary_ticket_id', models.PositiveIntegerField(blank=True, null=True)),
                ('ticket_status', models.CharField(default='pending', max_length=20)),
                ('ticket_error', models.TextField(blank=True)),
                ('backup_time', models.ForeignKey(limit_choices_to={'parent__code': 'SERVER_BACKUP_TIME'}, on_delete=django.db.models.deletion.PROTECT, related_name='mssql_clusters', to='project.choice')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('non_regulated_data', models.ManyToManyField(blank=True, limit_choices_to={'parent__code': 'NON_REGULATED_SENSITIVE_DATA'}, related_name='mssql_clusters_non_regulated', to='project.choice')),
                ('primary_server', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='primary_mssql_cluster', to='order.server')),
                ('regulated_data', models.ManyToManyField(blank=True, limit_choices_to={'parent__code': 'REGULATED_SENSITIVE_DATA'}, related_name='mssql_clusters_regulated', to='project.choice')),
                ('secondary_server', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='secondary_mssql_cluster', to='order.server')),
            ],
        ),
        migrations.CreateModel(
            name='MSSQLClusterDisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controller', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3')])) ,
                ('device_id', models.PositiveSmallIntegerField()),
                ('label', models.CharField(blank=True, max_length=100)),
                ('size_gb', models.PositiveIntegerField()),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disks', to='order.mssqlcluster')),
            ],
            options={'ordering': ('controller', 'device_id')},
        ),
        migrations.AddConstraint(
            model_name='mssqlclusterdisk',
            constraint=models.UniqueConstraint(fields=('cluster', 'controller', 'device_id'), name='unique_mssql_cluster_disk_device'),
        ),
        migrations.AddConstraint(
            model_name='mssqlclusterdisk',
            constraint=models.CheckConstraint(condition=models.Q(controller__in=(1, 2, 3)), name='mssql_cluster_controller_valid'),
        ),
        migrations.AddConstraint(
            model_name='mssqlclusterdisk',
            constraint=models.CheckConstraint(condition=~models.Q(device_id=7), name='mssql_cluster_device_not_seven'),
        ),
        migrations.AddConstraint(
            model_name='mssqlclusterdisk',
            constraint=models.CheckConstraint(condition=models.Q(size_gb__gt=0), name='mssql_cluster_disk_size_positive'),
        ),
        migrations.RunPython(add_windows_2025_choice, migrations.RunPython.noop),
    ]