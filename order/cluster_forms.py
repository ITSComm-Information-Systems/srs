import json
import re

from django import forms
from django.core.exceptions import ValidationError

from project.models import Choice, validate_shortcode
from .models import MSSQLCluster, MSSQLClusterDisk


CLUSTER_IDENTIFIER_PATTERN = re.compile(r'[tnp][da](?:0[1-9]|[1-9][0-9])')
CLUSTER_IDENTIFIER_ERROR = 'Enter an identifier such as td01, na23, or pd99.'


def normalize_cluster_identifier(value):
    identifier = value.strip().lower()
    if not CLUSTER_IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValidationError(CLUSTER_IDENTIFIER_ERROR)
    return identifier


class MSSQLClusterOrderForm(forms.Form):
    ENVIRONMENT_CHOICES = [
        ('t', 'Test'),
        ('n', 'Non-production'),
        ('p', 'Production'),
    ]
    INSTANCE_TYPE_CHOICES = [
        ('d', 'Database'),
        ('a', 'SSAS'),
    ]
    WINDOWS_CHOICES = [
        ('2022', 'Windows Server 2022'),
        ('2025', 'Windows Server 2025'),
    ]

    cluster_identifier = forms.CharField(
        label='Cluster identifier',
        max_length=4,
        help_text='Use environment (t/n/p), type (d/a), and sequence (01-99), for example td01.',
    )
    application = forms.CharField(max_length=100)
    cpu = forms.IntegerField(min_value=1, initial=2, help_text='MSSQL default: 2 vCPUs.')
    memory = forms.IntegerField(min_value=1, initial=4, label='Memory (GB)', help_text='MSSQL default: 4 GB. No 64 GB approval limit.')
    windows_version = forms.ChoiceField(choices=WINDOWS_CHOICES, initial='2022')
    backup_time = forms.ModelChoiceField(
        queryset=Choice.objects.filter(parent__code='SERVER_BACKUP_TIME', active=True).order_by('sequence'),
        label='Daily OS Backup Time',
    )
    shortcode = forms.CharField(min_length=6, max_length=6, label='Shortcode')
    additional_details = forms.CharField(required=False, widget=forms.Textarea)
    regulated_data = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.filter(parent__code='REGULATED_SENSITIVE_DATA', active=True).order_by('sequence'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    non_regulated_data = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.filter(parent__code='NON_REGULATED_SENSITIVE_DATA', active=True).order_by('sequence'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    disks_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        submitted_identifier = self.data.get('cluster_identifier') if self.is_bound else self.initial.get('cluster_identifier', '')
        environment = submitted_identifier.strip().lower()[:1] if submitted_identifier else ''
        self.fields['backup_time'].queryset = get_available_backup_times(environment)
        self.fields['cluster_identifier'].widget.attrs.update({
            'hx-get': '/orders/mssql-cluster/validate-identifier/',
            'hx-trigger': 'input changed delay:300ms',
            'hx-target': '#cluster-identifier-feedback',
            'hx-swap': 'outerHTML',
            'hx-sync': 'this:replace',
            'hx-include': '#id_backup_time',
            'aria-describedby': 'cluster-identifier-feedback',
        })
        for field in self.fields.values():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_cluster_identifier(self):
        return normalize_cluster_identifier(self.cleaned_data['cluster_identifier'])

    def clean_shortcode(self):
        shortcode = self.cleaned_data['shortcode'].strip()
        if not shortcode.isdigit():
            raise ValidationError('Shortcode must contain exactly six digits.')
        validate_shortcode(shortcode)
        return shortcode

    def clean_disks_json(self):
        value = self.cleaned_data.get('disks_json') or '[]'
        try:
            disks = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            raise ValidationError('Disk configuration is invalid.')

        if not isinstance(disks, list):
            raise ValidationError('Disk configuration must be a list.')

        seen = set()
        for index, disk in enumerate(disks, start=1):
            if not isinstance(disk, dict):
                raise ValidationError(f'Disk {index} is invalid.')
            try:
                controller = int(disk['controller'])
                device_id = int(disk['device_id'])
                size_gb = int(disk['size_gb'])
            except (KeyError, TypeError, ValueError):
                raise ValidationError(f'Disk {index} needs a controller, device ID, and size.')

            if controller not in (1, 2, 3):
                raise ValidationError(f'Disk {index} has an unsupported SCSI controller.')
            allowed_device_ids = {value for value, _label in MSSQLClusterDisk.DEVICE_ID_CHOICES}
            if device_id not in allowed_device_ids:
                raise ValidationError(f'Disk {index} device ID must be selected from the available IDs; ID 7 is reserved.')
            if size_gb <= 0:
                raise ValidationError(f'Disk {index} size must be greater than zero.')
            key = (controller, device_id)
            if key in seen:
                raise ValidationError(f'Device ID {device_id} is duplicated on controller {controller}.')
            seen.add(key)

            label = disk.get('label', '')
            if not isinstance(label, str) or len(label) > 100:
                raise ValidationError(f'Disk {index} label must be text of at most 100 characters.')
            disk.update(controller=controller, device_id=device_id, size_gb=size_gb, label=label.strip())

        identifier = self.cleaned_data.get('cluster_identifier', '')
        if len(identifier) == 4 and identifier[1] == 'a' and any(disk['controller'] == 2 for disk in disks):
            raise ValidationError('SSAS cluster disks may use controllers 1 or 3 only.')
        return disks

    @staticmethod
    def _minutes(label):
        match = re.search(r'(?<!\d)(\d{1,2}):(\d{2})\s*(AM|PM)?', label, re.IGNORECASE)
        if not match:
            return None
        hour, minute = int(match.group(1)), int(match.group(2))
        period = (match.group(3) or '').upper()
        if minute > 59 or hour > (12 if period else 23):
            return None
        if period:
            hour %= 12
            if period == 'PM':
                hour += 12
        return hour * 60 + minute

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get('cluster_identifier')
        backup_time = cleaned.get('backup_time')
        if not identifier or not backup_time:
            return cleaned

        backup_minutes = self._minutes(backup_time.label)
        if backup_minutes is None:
            self.add_error('backup_time', 'The selected backup choice does not contain a recognized time.')
            return cleaned

        patch_window = get_cluster_patch_window(identifier[0])
        if patch_window is None:
            self.add_error(None, 'Required patch-day or patch-time choices are not configured in SRS.')
            return cleaned

        for patch_minute in (
            self._minutes(patch_window['primary_time'].label),
            self._minutes(patch_window['secondary_time'].label),
        ):
            distance = abs(backup_minutes - patch_minute)
            distance = min(distance, 1440 - distance)
            if distance < 120:
                self.add_error('backup_time', 'Daily OS backup must be at least two hours from both servers’ patch times.')
                break
        return cleaned

    @property
    def cluster_values(self):
        identifier = self.cleaned_data['cluster_identifier']
        return {
            'environment': identifier[0],
            'instance_type': identifier[1],
            'sequence': identifier[2:],
            'cluster_name': f'db-{identifier}-c',
            'primary_name': f'db-{identifier}-cm1',
            'secondary_name': f'db-{identifier}-ca1',
        }


def get_cluster_patch_window(environment):
    day_name = 'Sunday' if environment == 'p' else 'Thursday'
    day_choice = next(
        (
            choice for choice in Choice.objects.filter(parent__code='SERVER_PATCH_DATE', active=True)
            if choice.label.casefold().startswith(day_name.casefold())
        ),
        None,
    )
    patch_choices = {
        MSSQLClusterOrderForm._minutes(choice.label): choice
        for choice in Choice.objects.filter(parent__code='SERVER_PATCH_TIME', active=True)
    }
    primary_time = patch_choices.get(120) or patch_choices.get(180)
    secondary_time = patch_choices.get(300)
    if not day_choice or not primary_time or not secondary_time:
        return None
    return {
        'day': day_choice,
        'primary_time': primary_time,
        'secondary_time': secondary_time,
    }


def get_available_backup_times(environment):
    queryset = Choice.objects.filter(
        parent__code='SERVER_BACKUP_TIME', active=True
    ).order_by('sequence')
    if environment not in {'t', 'n', 'p'}:
        return queryset

    patch_window = get_cluster_patch_window(environment)
    if not patch_window:
        return queryset

    patch_minutes = (
        MSSQLClusterOrderForm._minutes(patch_window['primary_time'].label),
        MSSQLClusterOrderForm._minutes(patch_window['secondary_time'].label),
    )
    available_ids = [
        choice.pk
        for choice in queryset
        if (backup_minutes := MSSQLClusterOrderForm._minutes(choice.label)) is not None
        and all(
            min(abs(backup_minutes - patch_minute), 1440 - abs(backup_minutes - patch_minute)) >= 120
            for patch_minute in patch_minutes
        )
    ]
    return queryset.filter(pk__in=available_ids)


class MSSQLClusterDiskForm(forms.ModelForm):
    class Meta:
        model = MSSQLClusterDisk
        fields = ('controller', 'device_id', 'label', 'size_gb')

    def __init__(self, *args, cluster, **kwargs):
        self.cluster = cluster
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if cluster.instance_type == 'a':
            self.fields['controller'].choices = [(1, '1'), (3, '3')]

    def clean(self):
        cleaned = super().clean()
        controller = cleaned.get('controller')
        device_id = cleaned.get('device_id')
        if controller == 2 and self.cluster.instance_type == 'a':
            self.add_error('controller', 'SSAS cluster disks may use controllers 1 or 3 only.')
        if device_id == 7:
            self.add_error('device_id', 'Device ID 7 is reserved and cannot be used.')
        if device_id is not None and controller is not None:
            duplicate = MSSQLClusterDisk.objects.filter(
                cluster=self.cluster, controller=controller, device_id=device_id
            ).exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error('device_id', 'This device ID is already in use on the selected controller.')
        if self.instance.pk and cleaned.get('size_gb', 0) < self.instance.size_gb:
            self.add_error('size_gb', 'Disk size cannot be decreased.')
        return cleaned


class MSSQLClusterEditForm(forms.ModelForm):
    """Edit the mutable cluster-level configuration after an order is placed."""

    class Meta:
        model = MSSQLCluster
        fields = (
            'application',
            'cpu',
            'memory',
            'windows_version',
            'shortcode',
            'additional_details',
            'regulated_data',
            'non_regulated_data',
        )
        widgets = {
            'additional_details': forms.Textarea(attrs={'rows': 3}),
            'regulated_data': forms.CheckboxSelectMultiple,
            'non_regulated_data': forms.CheckboxSelectMultiple,
        }
        labels = {
            'memory': 'Memory (GB)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['regulated_data'].queryset = Choice.objects.filter(
            parent__code='REGULATED_SENSITIVE_DATA', active=True
        ).order_by('sequence')
        self.fields['non_regulated_data'].queryset = Choice.objects.filter(
            parent__code='NON_REGULATED_SENSITIVE_DATA', active=True
        ).order_by('sequence')
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_shortcode(self):
        shortcode = self.cleaned_data['shortcode'].strip()
        if not shortcode.isdigit() or len(shortcode) != 6:
            raise ValidationError('Shortcode must contain exactly six digits.')
        validate_shortcode(shortcode)
        return shortcode

    def save(self, commit=True):
        cluster = super().save(commit=commit)
        if commit:
            # Keep both MiServer records in sync with shared cluster values.
            servers = [cluster.primary_server, cluster.secondary_server]
            for server in servers:
                server.cpu = cluster.cpu
                server.ram = cluster.memory
                server.shortcode = cluster.shortcode
                server.save(update_fields=['cpu', 'ram', 'shortcode'])
                server.regulated_data.set(self.cleaned_data['regulated_data'])
                server.non_regulated_data.set(self.cleaned_data['non_regulated_data'])
        return cluster