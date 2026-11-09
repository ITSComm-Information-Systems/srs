import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction, models
from django.http import HttpResponseForbidden, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from copy import copy

from oscauth.models import LDAPGroup, LDAPGroupMember
from order.cluster_forms import (
    MSSQLClusterDiskForm,
    MSSQLClusterEditForm,
    MSSQLClusterOrderForm,
    get_available_backup_times,
    get_cluster_patch_window,
    normalize_cluster_identifier,
)
from order.models import MSSQLCluster, MSSQLClusterDisk, Server, ServerDisk
from project.integrations import MCommunity, TDx, create_ticket, create_ticket_server_delete, ServerPayload
from project.models import Choice


DBA_GROUP_NAME = 'its mssqldba'
logger = logging.getLogger(__name__)


class ClusterChangeTicketError(Exception):
    pass


def is_mssql_dba(user):
    if not user.is_authenticated:
        return False
    try:
        community = MCommunity()
        community.get_group(DBA_GROUP_NAME)
        return user.username in getattr(community, 'members', set())
    except Exception:
        return False


def user_cluster_queryset(user):
    """Clusters whose owning MiServer group the user belongs to."""
    user_group_ids = LDAPGroupMember.objects.filter(
        username=user.username
    ).values_list('ldap_group_id', flat=True)
    return MSSQLCluster.objects.select_related(
        'primary_server', 'secondary_server'
    ).filter(primary_server__owner_id__in=user_group_ids)


def format_cluster_patch_window(identifier):
    try:
        identifier = normalize_cluster_identifier(identifier)
    except ValidationError:
        return ''

    patch_window = get_cluster_patch_window(identifier[0])
    if not patch_window:
        return 'Patch-window choices are not configured.'

    day = patch_window['day'].label
    return (
        f'Primary MACC: {day} at {patch_window["primary_time"].label}; '
        f'Secondary ASB: {day} at {patch_window["secondary_time"].label}'
    )


def get_windows_choice(version):
    code = f'Windows{version}managed'
    choice = Choice.objects.filter(code__iexact=code, active=True).first()
    if choice:
        return choice
    return Choice.objects.filter(
        parent__code__in=('WINDOWS', 'SERVER_UNMANAGED_OS'),
        label__icontains=version,
        active=True,
    ).first()


def get_cluster_ticket_config():
    config = {'FormID': ServerPayload.form_id, 
              'TypeID': ServerPayload.type_id,
              'ServiceID': ServerPayload.service_id,
              'ResponsibleGroupID': ServerPayload.responsible_group_id}
    required = ('FormID', 'TypeID', 'ServiceID', 'ResponsibleGroupID')
    if not isinstance(config, dict) or any(not config.get(key) for key in required):
        raise ImproperlyConfigured(
            'Configure MSSQL_CLUSTER_TDX with FormID, TypeID, ServiceID, and the VCI ResponsibleGroupID.'
        )
    try:
        return {key: int(config[key]) for key in required}
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured('MSSQL_CLUSTER_TDX values must be integer IDs.') from exc


def cluster_ticket_payload(cluster, request, config):
    disk_lines = [
        f'SCSI {disk.controller}:{disk.device_id} - {disk.label} - {disk.size_gb} GB'
        for disk in cluster.disks.all()
    ]
    sensitivity = [
        choice.label
        for choice in list(cluster.regulated_data.all()) + list(cluster.non_regulated_data.all())
    ]
    description = '\n'.join([
        f'Cluster: {cluster.name}',
        f'Application: {cluster.application}',
        f'Instance type: {cluster.get_instance_type_display()}',
        f'VM cluster: {cluster.vm_cluster}',
        f'CPU: {cluster.cpu}',
        f'Memory: {cluster.memory} GB',
        f'Shortcode: {cluster.shortcode}',
        f'Windows version: {cluster.windows_version}',
        f'Daily OS backup time: {cluster.backup_time.label}',
        f'Primary MACC server: {cluster.primary_server.name}',
        f'Secondary ASB server: {cluster.secondary_server.name}',
        f'Data sensitivity: {", ".join(sensitivity) if sensitivity else "None selected"}',
        'Regulated data: ' + ', '.join(
            f'{choice.label} (ID {choice.pk})' for choice in cluster.regulated_data.all()
        ),
        'Non-regulated data: ' + ', '.join(
            f'{choice.label} (ID {choice.pk})' for choice in cluster.non_regulated_data.all()
        ),
        'Cluster disks:',
        *(disk_lines or ['None']),
        f'Additional details: {cluster.additional_details}',
    ])
    return {
        'FormID': config['FormID'],
        'TypeID': config['TypeID'],
        'SourceID': 4,
        'StatusID': 77,
        'PriorityID': 20,
        'ServiceID': config['ServiceID'],
        'ResponsibleGroupID': config['ResponsibleGroupID'],
        'Title': f'MSSQL Cluster Request - {cluster.name}',
        'RequestorEmail': cluster.created_by.email,
        'Description': description,
        'Attributes': [],
    }


def submit_cluster_change_ticket(cluster, request, config, operation, before, after):
    try:
        payload = cluster_ticket_payload(cluster, request, config)
        payload.update({
            'Title': f'MSSQL Cluster Change - {cluster.name} - {operation}',
            'RequestorEmail': request.user.email,
            'Description': '\n'.join([
                f'Operation: {operation}',
                f'Original cluster ticket: {cluster.cluster_ticket_id or "Not recorded"}',
                f'Requested by: {request.user.username}',
                '', 'Before:', before, '', 'After:', after,
            ]),
        })
        response = TDx().create_ticket(payload)
        if not response.ok:
            raise RuntimeError(f'TDX returned HTTP {response.status_code}')
        return response.json()['ID']
    except Exception as exc:
        logger.exception('TDX change ticket failed for cluster %s', cluster.pk)
        raise ClusterChangeTicketError from exc


def submit_cluster_tickets(cluster, request, config):
    cluster.ticket_status = 'in_progress'
    cluster.save(update_fields=['ticket_status'])

    if not cluster.cluster_ticket_id:
        response = TDx().create_ticket(cluster_ticket_payload(cluster, request, config))
        if not response.ok:
            raise RuntimeError(f'Cluster TDX ticket failed: {response.status_code} {response.text}')
        cluster.cluster_ticket_id = response.json()['ID']
        cluster.save(update_fields=['cluster_ticket_id'])

    description = (
        f'MSSQL cluster {cluster.name}\n'
        f'Application: {cluster.application}\n'
        f'Instance type: {cluster.get_instance_type_display()}\n'
        f'Cluster ticket: {cluster.cluster_ticket_id}\n'
        'Cluster disks:\n' + '\n'.join(
            f'SCSI {disk.controller}:{disk.device_id} - {disk.label} - {disk.size_gb} GB'
            for disk in cluster.disks.all()
        ) + '\nData sensitivity: ' + ', '.join(
            choice.label
            for choice in list(cluster.regulated_data.all()) + list(cluster.non_regulated_data.all())
        )
    )
    server_request = copy(request)
    server_request.user = cluster.created_by
    server_request.POST = QueryDict('consultation=No', mutable=False)
    if not cluster.primary_ticket_id:
        primary_ticket = create_ticket('New', cluster.primary_server, server_request, Description=description)
        cluster.primary_ticket_id = primary_ticket['ID']
        cluster.save(update_fields=['primary_ticket_id'])

    if not cluster.secondary_ticket_id:
        secondary_ticket = create_ticket('New', cluster.secondary_server, server_request, Description=description)
        cluster.secondary_ticket_id = secondary_ticket['ID']
        cluster.save(update_fields=['secondary_ticket_id'])
    cluster.ticket_status = 'submitted'
    cluster.ticket_error = ''
    cluster.save(update_fields=['secondary_ticket_id', 'ticket_status', 'ticket_error'])


def create_cluster_records(form, request):
    values = form.cluster_values
    cleaned = form.cleaned_data
    dba_group = LDAPGroup.objects.filter(name__iexact=DBA_GROUP_NAME).first()
    if not dba_group:
        dba_group = LDAPGroup().lookup(DBA_GROUP_NAME)
    if not dba_group:
        raise ValidationError('The its mssqldba MCommunity group is not available in SRS.')

    os_choice = get_windows_choice(cleaned['windows_version'])
    if not os_choice:
        raise ValidationError(
            f'Windows Server {cleaned["windows_version"]} is not configured in the MiServer operating-system choices.'
        )

    patch_window = get_cluster_patch_window(values['environment'])
    if not patch_window:
        raise ValidationError('Required MiServer patch-day or patch-time choices are not configured.')
    primary_day = secondary_day = patch_window['day']
    primary_time = patch_window['primary_time']
    secondary_time = patch_window['secondary_time']

    database_type = None
    if values['instance_type'] == 'd':
        database_type = Choice.objects.filter(parent__code='DATABASE_TYPE', code__iexact='MSSQL').first()

    backup_time = cleaned['backup_time']
    on_call = Server.ALL_HOURS if values['environment'] == 'p' else Server.BUSINESS_HOURS
    common = {
        'owner': dba_group,
        'admin_group': dba_group,
        'database_type': database_type,
        'cluster_instance_type': values['instance_type'],
        'shortcode': cleaned['shortcode'],
        'public_facing': False,
        'production': values['environment'] == 'p',
        'managed': True,
        'os': os_choice,
        'cpu': cleaned['cpu'],
        'ram': cleaned['memory'],
        'replicated': True,
        'on_call': on_call,
        'in_service': True,
        'billable': False,
        'firewall': ' ',
        'backup': True,
        'support_email': 'its.mssqldba@umich.edu',
        'support_phone': '734-822-7754',
        'backup_time': backup_time,
        'reboot_time': None,
        'reboot_day': None,
        'domain': 'umich.edu',
        'firewall_requests': ' ',
    }

    primary_server = Server.objects.create(
        name=values['primary_name'], datacenter='MACC', patch_day=primary_day,
        patch_time=primary_time, **common,
    )
    secondary_server = Server.objects.create(
        name=values['secondary_name'], datacenter='ASB', patch_day=secondary_day,
        patch_time=secondary_time, **common,
    )
    ServerDisk.objects.create(server=primary_server, name='disk0', controller=0, device=0, size=50)
    ServerDisk.objects.create(server=secondary_server, name='disk0', controller=0, device=0, size=50)

    for server in (primary_server, secondary_server):
        server.regulated_data.set(cleaned['regulated_data'])
        server.non_regulated_data.set(cleaned['non_regulated_data'])

    cluster = MSSQLCluster(
        name=values['cluster_name'],
        environment=values['environment'],
        instance_type=values['instance_type'],
        sequence=values['sequence'],
        application=cleaned['application'],
        vm_cluster='mssqlcluster',
        cpu=cleaned['cpu'],
        memory=cleaned['memory'],
        windows_version=cleaned['windows_version'],
        backup_time=backup_time,
        shortcode=cleaned['shortcode'],
        additional_details=cleaned['additional_details'],
        primary_server=primary_server,
        secondary_server=secondary_server,
        created_by=request.user,
    )
    cluster.full_clean()
    cluster.save()
    cluster.regulated_data.set(cleaned['regulated_data'])
    cluster.non_regulated_data.set(cleaned['non_regulated_data'])
    for disk in cleaned['disks_json']:
        cluster_disk = MSSQLClusterDisk(cluster=cluster, **disk)
        cluster_disk.full_clean()
        cluster_disk.save()
    return cluster


class MSSQLClusterOrderView(View):
    template_name = 'order/mssql_cluster_order.html'

    def dispatch(self, request, *args, **kwargs):
        if not is_mssql_dba(request.user):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('MSSQL Cluster ordering is restricted to the DBA team.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        clusters = user_cluster_queryset(request.user).order_by('-created_date')
        return render(request, self.template_name, {
            'form': MSSQLClusterOrderForm(),
            'clusters': clusters,
            'patch_window': '',
        })

    def post(self, request):
        form = MSSQLClusterOrderForm(request.POST)
        patch_window_preview = format_cluster_patch_window(request.POST.get('cluster_identifier', ''))
        if not form.is_valid():
            return render(request, self.template_name, {
                'form': form,
                'patch_window': patch_window_preview,
            })

        try:
            get_cluster_ticket_config()
            cluster_name = form.cluster_values['cluster_name']
            if MSSQLCluster.objects.filter(name__iexact=cluster_name).exists():
                form.add_error('cluster_identifier', 'This cluster name is already in use.')
                return render(request, self.template_name, {'form': form, 'patch_window': patch_window_preview})
            hostnames = (form.cluster_values['primary_name'], form.cluster_values['secondary_name'])
            if Server.objects.filter(
                models.Q(name__iexact=hostnames[0]) | models.Q(name__iexact=hostnames[1])
            ).exists():
                form.add_error('cluster_identifier', 'One or both generated server names are already in use.')
                return render(request, self.template_name, {'form': form, 'patch_window': patch_window_preview})
            with transaction.atomic():
                cluster = create_cluster_records(form, request)
        except (ImproperlyConfigured, ValidationError) as exc:
            return render(request, self.template_name, {
                'form': form,
                'patch_window': patch_window_preview,
                'error_message': str(exc),
            })

        try:
            submit_cluster_tickets(cluster, request, get_cluster_ticket_config())
        except Exception as exc:
            cluster.ticket_status = 'failed'
            cluster.ticket_error = str(exc)[:4000]
            cluster.save(update_fields=['ticket_status', 'ticket_error'])
            return render(request, self.template_name, {
                'form': form,
                'cluster': cluster,
                'patch_window': patch_window_preview,
                'error_message': f'Cluster {cluster.name} was saved, but ticket submission did not complete. '
                                 f'Use the cluster management page to retry missing tickets. {exc}',
            })

        return render(request, 'order/mssql_cluster_submitted.html', {'cluster': cluster})


class MSSQLClusterIdentifierValidationView(View):
    def get(self, request):
        if not LDAPGroupMember.objects.filter(
            username=request.user.username,
            ldap_group__name__iexact=DBA_GROUP_NAME,
        ).exists():
            return HttpResponseForbidden('MSSQL Cluster ordering is restricted to the DBA team.')

        error = ''
        identifier = request.GET.get('cluster_identifier', '')
        environment = ''
        try:
            environment = normalize_cluster_identifier(identifier)[0]
        except ValidationError as exc:
            error = exc.messages[0]
        backup_time_choices = list(get_available_backup_times(environment))
        selected_backup_time_id = request.GET.get('backup_time', '')
        selected_backup_time = next(
            (choice for choice in backup_time_choices if str(choice.pk) == selected_backup_time_id),
            None,
        )
        return render(request, 'order/_cluster_identifier_validation_response.html', {
            'error': error,
            'patch_window': format_cluster_patch_window(identifier),
            'backup_time_choices': backup_time_choices,
            'selected_backup_time': selected_backup_time,
        })


def delete_cluster_with_tickets(cluster_id, request):
    config = get_cluster_ticket_config()
    ticket_ids = []
    for field_name, server_field in (
        ('delete_cluster_ticket_id', None),
        ('delete_primary_ticket_id', 'primary_server'),
        ('delete_secondary_ticket_id', 'secondary_server'),
    ):
        with transaction.atomic():
            cluster = get_object_or_404(
                user_cluster_queryset(request.user).select_for_update(), pk=cluster_id,
            )
            ticket_id = getattr(cluster, field_name)
            if not ticket_id:
                if server_field is None:
                    before = cluster_ticket_payload(cluster, request, config)['Description']
                    ticket_id = submit_cluster_change_ticket(
                        cluster, request, config, 'Decommission cluster', before,
                        'Cluster and shared disk records removed from SRS; '
                        'both MiServers marked out of service. '
                        'Decommission both servers and their shared storage through TDX.',
                    )
                else:
                    server = getattr(cluster, server_field)
                    response = create_ticket_server_delete(
                        server, request.user,
                        f'End Service for {server.name} - MSSQL cluster {cluster.name}. '
                        f'Cluster decommission ticket: {cluster.delete_cluster_ticket_id}. '
                        'Coordinate shared storage removal with the DBA team.',
                    )
                    if not response.ok:
                        raise ClusterChangeTicketError(f'TDX returned HTTP {response.status_code}')
                    ticket_id = response.json()['ID']
                ticket_id = int(ticket_id)
                if ticket_id <= 0:
                    raise ClusterChangeTicketError('TDX did not return a valid ticket ID.')
                setattr(cluster, field_name, ticket_id)
                cluster.ticket_status = 'deleting'
                cluster.ticket_error = ''
                cluster.save(update_fields=[field_name, 'ticket_status', 'ticket_error'])
            ticket_ids.append(ticket_id)

    with transaction.atomic():
        cluster = get_object_or_404(
            user_cluster_queryset(request.user).select_for_update(), pk=cluster_id,
        )
        cluster_name = cluster.name
        for server_id in (cluster.primary_server_id, cluster.secondary_server_id):
            server = Server.objects.select_for_update().get(pk=server_id)
            if server.in_service:
                server.name = f'{server.name}-Ended-{timezone.localdate():%Y%m%d}'
                server.in_service = False
                server.save(update_fields=['name', 'in_service'])
        cluster.delete()
    return cluster_name, ticket_ids


class MSSQLClusterManageView(View):
    def dispatch(self, request, *args, **kwargs):
        if not is_mssql_dba(request.user):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('MSSQL Cluster management is restricted to the DBA team.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, cluster_id):
        cluster = get_object_or_404(user_cluster_queryset(request.user), pk=cluster_id)
        return render(request, 'order/mssql_cluster_manage.html', {
            'cluster': cluster,
            'disk_form': MSSQLClusterDiskForm(cluster=cluster),
            'cluster_form': MSSQLClusterEditForm(instance=cluster),
        })

    def post(self, request, cluster_id):
        cluster = get_object_or_404(user_cluster_queryset(request.user), pk=cluster_id)
        if cluster.ticket_status in ('deleting', 'delete_failed'):
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': MSSQLClusterEditForm(instance=cluster),
                'error_message': 'Cluster deletion has started. Retry deletion from the cluster list.',
            }, status=409)
        operation = request.POST.get('operation')
        if operation == 'retry_tickets':
            return self.process_change(request, cluster)
        operations = {
            'edit_cluster': 'Update configuration',
            'add': 'Add disk',
            'save': 'Update disk',
            'remove': 'Remove disk',
        }
        if operation not in operations:
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest('Unknown cluster operation.')
        try:
            config = get_cluster_ticket_config()
        except ImproperlyConfigured:
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': MSSQLClusterEditForm(instance=cluster),
                'error_message': 'Ticket routing is not configured. No changes were saved.',
            })
        try:
            with transaction.atomic():
                cluster = user_cluster_queryset(request.user).select_for_update().get(pk=cluster.pk)
                if cluster.ticket_status in ('deleting', 'delete_failed'):
                    from django.http import HttpResponse
                    return HttpResponse('Cluster deletion has started.', status=409)
                before = cluster_ticket_payload(cluster, request, config)['Description']
                response = self.process_change(request, cluster)
                cluster.refresh_from_db()
                after = cluster_ticket_payload(cluster, request, config)['Description']
                if before == after:
                    return response
                ticket_id = submit_cluster_change_ticket(
                    cluster, request, config, operations[operation], before, after,
                )
        except ClusterChangeTicketError:
            cluster.refresh_from_db()
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': MSSQLClusterEditForm(instance=cluster),
                'error_message': 'The change was not saved because its TDX ticket could not be confirmed. '
                                 'Check TDX before retrying if the submission timed out.',
            })
        return render(request, 'order/mssql_cluster_manage.html', {
            'cluster': cluster,
            'disk_form': MSSQLClusterDiskForm(cluster=cluster),
            'cluster_form': MSSQLClusterEditForm(instance=cluster),
            'notice': f'Cluster change saved. TDX ticket {ticket_id} created.',
        })

    def process_change(self, request, cluster):
        operation = request.POST.get('operation')

        if operation == 'retry_tickets':
            try:
                submit_cluster_tickets(cluster, request, get_cluster_ticket_config())
                return render(request, 'order/mssql_cluster_manage.html', {
                    'cluster': cluster,
                    'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                    'cluster_form': MSSQLClusterEditForm(instance=cluster),
                    'notice': 'All cluster and MiServer tickets are recorded.',
                })
            except Exception as exc:
                cluster.refresh_from_db()
                cluster.ticket_status = 'failed'
                cluster.ticket_error = str(exc)[:4000]
                cluster.save(update_fields=['ticket_status', 'ticket_error'])
                return render(request, 'order/mssql_cluster_manage.html', {
                    'cluster': cluster,
                    'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                    'cluster_form': MSSQLClusterEditForm(instance=cluster),
                    'error_message': str(exc),
                })

        if operation == 'edit_cluster':
            cluster_form = MSSQLClusterEditForm(request.POST, instance=cluster)
            if cluster_form.is_valid():
                os_choice = get_windows_choice(cluster_form.cleaned_data['windows_version'])
                if not os_choice:
                    cluster_form.add_error(
                        'windows_version',
                        f'Windows Server {cluster_form.cleaned_data["windows_version"]} is not configured '
                        'in the MiServer operating-system choices.',
                    )
                else:
                    with transaction.atomic():
                        cluster = cluster_form.save()
                        for server in (cluster.primary_server, cluster.secondary_server):
                            server.os = os_choice
                            server.save(update_fields=['os'])
                    return render(request, 'order/mssql_cluster_manage.html', {
                        'cluster': cluster,
                        'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                        'cluster_form': MSSQLClusterEditForm(instance=cluster),
                        'notice': 'Cluster configuration updated.',
                    })
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': cluster_form,
                'show_cluster_edit': True,
            })

        disk_id = request.POST.get('disk_id')
        if operation == 'remove':
            disk = get_object_or_404(MSSQLClusterDisk, pk=disk_id, cluster=cluster)
            disk.delete()
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': MSSQLClusterEditForm(instance=cluster),
                'notice': 'Cluster disk removed.',
            })

        instance = get_object_or_404(MSSQLClusterDisk, pk=disk_id, cluster=cluster) if disk_id else None
        form = MSSQLClusterDiskForm(request.POST, instance=instance, cluster=cluster)
        if form.is_valid():
            disk = form.save(commit=False)
            disk.cluster = cluster
            disk.save()
            return render(request, 'order/mssql_cluster_manage.html', {
                'cluster': cluster,
                'disk_form': MSSQLClusterDiskForm(cluster=cluster),
                'cluster_form': MSSQLClusterEditForm(instance=cluster),
                'notice': 'Cluster disk saved.',
            })
        return render(request, 'order/mssql_cluster_manage.html', {
            'cluster': cluster,
            'disk_form': form,
            'cluster_form': MSSQLClusterEditForm(instance=cluster),
        })


class MSSQLClusterListView(View):
    template_name = 'order/mssql_cluster_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not is_mssql_dba(request.user):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('MSSQL Cluster management is restricted to the DBA team.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        clusters = user_cluster_queryset(request.user).order_by('-created_date')
        return render(request, self.template_name, {
            'clusters': clusters,
        })

    def post(self, request):
        if request.POST.get('operation') != 'delete_cluster':
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest('Unknown cluster operation.')
        cluster = get_object_or_404(
            user_cluster_queryset(request.user), pk=request.POST.get('cluster_id'),
        )
        try:
            cluster_name, ticket_ids = delete_cluster_with_tickets(cluster.pk, request)
        except Exception:
            logger.exception('Cluster deletion failed for cluster %s', cluster.pk)
            user_cluster_queryset(request.user).filter(pk=cluster.pk).update(
                ticket_status='delete_failed',
                ticket_error='Deletion could not be completed. Confirmed tickets are retained. '
                             'Check TDX before retrying if a submission timed out.',
            )
            return render(request, self.template_name, {
                'clusters': user_cluster_queryset(request.user).order_by('-created_date'),
                'error_message': 'The cluster was not deleted. Confirmed deletion tickets have been '
                                 'retained for retry. Check TDX before retrying a timed-out submission.',
            }, status=502)
        messages.success(
            request,
            f'Cluster {cluster_name} deleted from SRS and both MiServers marked out of service. '
            f'TDX tickets: {", ".join(str(ticket_id) for ticket_id in ticket_ids)}.',
        )
        return redirect('/orders/mssql-cluster/list/')

