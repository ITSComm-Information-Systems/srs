import json
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from order.cluster_forms import (
	MSSQLClusterOrderForm,
	get_available_backup_times,
	get_cluster_patch_window,
	normalize_cluster_identifier,
)
from order.cluster_views import format_cluster_patch_window
from order.models import MSSQLClusterDisk
from project.models import Choice


class MSSQLClusterOrderFormTests(TestCase):
	def setUp(self):
		shortcode_validator = patch('order.cluster_forms.validate_shortcode')
		shortcode_validator.start()
		self.addCleanup(shortcode_validator.stop)
		backup_group = Choice.objects.create(code='SERVER_BACKUP_TIME', label='Server Backup Time', sequence=1)
		patch_group = Choice.objects.create(code='SERVER_PATCH_TIME', label='Server Patch Time', sequence=1)
		patch_day_group = Choice.objects.create(code='SERVER_PATCH_DATE', label='Server Patch Day', sequence=1)
		self.backup_3am = Choice.objects.create(
			code='0300', label='3:00 AM', sequence=1, parent=backup_group
		)
		self.backup_4am = Choice.objects.create(
			code='0400', label='4:00 AM', sequence=2, parent=backup_group
		)
		self.backup_7am = Choice.objects.create(
			code='0700', label='7:00 AM', sequence=3, parent=backup_group
		)
		for sequence, label in enumerate(('2:00 AM', '3:00 AM', '5:00 AM'), start=1):
			Choice.objects.create(code=f'PATCH{sequence}', label=label, sequence=sequence, parent=patch_group)
		Choice.objects.create(code='SUN', label='Sunday', sequence=1, parent=patch_day_group)
		Choice.objects.create(code='THU', label='Thursday', sequence=2, parent=patch_day_group)

	def form_data(self, **overrides):
		data = {
			'cluster_identifier': 'td01',
			'application': 'eResearch',
			'cpu': '4',
			'memory': '32',
			'windows_version': '2022',
			'backup_time': str(self.backup_7am.pk),
			'shortcode': '123456',
			'additional_details': '',
			'disks_json': json.dumps([
				{'controller': 1, 'device_id': 0, 'label': 'Root TranLog', 'size_gb': 100}
			]),
		}
		data.update(overrides)
		return data

	def test_identifier_generates_cluster_and_hosts(self):
		form = MSSQLClusterOrderForm(self.form_data())

		self.assertTrue(form.is_valid(), form.errors)
		self.assertEqual(form.cluster_values['cluster_name'], 'db-td01-c')
		self.assertEqual(form.cluster_values['primary_name'], 'db-td01-cm1')
		self.assertEqual(form.cluster_values['secondary_name'], 'db-td01-ca1')

	def test_invalid_identifier_is_rejected(self):
		form = MSSQLClusterOrderForm(self.form_data(cluster_identifier='xd00'))

		self.assertFalse(form.is_valid())
		self.assertIn('cluster_identifier', form.errors)

	def test_identifier_normalization_and_boundaries(self):
		for identifier in ('td01', 'na23', 'pd99', ' TD01 '):
			with self.subTest(identifier=identifier):
				self.assertIn(normalize_cluster_identifier(identifier), ('td01', 'na23', 'pd99'))

		for identifier in ('td00', 'td100', 'xd01', 'tx01', 'td1', 'td001'):
			with self.subTest(identifier=identifier):
				with self.assertRaises(ValidationError):
					normalize_cluster_identifier(identifier)

	def test_patch_window_uses_environment_and_configured_primary_fallback(self):
		production_window = get_cluster_patch_window('p')
		nonproduction_window = get_cluster_patch_window('n')

		self.assertEqual(production_window['day'].label, 'Sunday')
		self.assertEqual(production_window['primary_time'].label, '2:00 AM')
		self.assertEqual(production_window['secondary_time'].label, '5:00 AM')
		self.assertEqual(nonproduction_window['day'].label, 'Thursday')
		self.assertIn('Primary MACC: Sunday at 2:00 AM', format_cluster_patch_window('pd01'))

		Choice.objects.filter(code='PATCH1').update(active=False)
		fallback_window = get_cluster_patch_window('p')
		self.assertEqual(fallback_window['primary_time'].label, '3:00 AM')

	def test_backup_time_choices_exclude_times_within_two_hours_of_patch(self):
		available_ids = set(
			get_available_backup_times('p').values_list('pk', flat=True)
		)

		self.assertNotIn(self.backup_3am.pk, available_ids)
		self.assertNotIn(self.backup_4am.pk, available_ids)
		self.assertIn(self.backup_7am.pk, available_ids)

	def test_device_id_seven_is_reserved(self):
		form = MSSQLClusterOrderForm(self.form_data(disks_json=json.dumps([
			{'controller': 1, 'device_id': 7, 'label': '', 'size_gb': 100}
		])))

		self.assertFalse(form.is_valid())
		self.assertIn('disks_json', form.errors)

	def test_device_id_dropdown_excludes_reserved_seven(self):
		device_choices = {value for value, _label in MSSQLClusterDisk.DEVICE_ID_CHOICES}

		self.assertEqual(device_choices, set(range(16)) - {7})

	def test_duplicate_device_ids_on_same_controller_are_rejected(self):
		form = MSSQLClusterOrderForm(self.form_data(disks_json=json.dumps([
			{'controller': 1, 'device_id': 0, 'label': '', 'size_gb': 100},
			{'controller': 1, 'device_id': 0, 'label': '', 'size_gb': 200},
		])))

		self.assertFalse(form.is_valid())
		self.assertIn('disks_json', form.errors)

	def test_ssas_cannot_use_controller_two(self):
		form = MSSQLClusterOrderForm(self.form_data(
			cluster_identifier='ta01',
			disks_json=json.dumps([
				{'controller': 2, 'device_id': 0, 'label': '', 'size_gb': 100}
			]),
		))

		self.assertFalse(form.is_valid())
		self.assertIn('disks_json', form.errors)

	def test_backup_must_be_two_hours_from_each_host_patch(self):
		too_close = MSSQLClusterOrderForm(self.form_data(backup_time=str(self.backup_4am.pk)))
		valid_boundary = MSSQLClusterOrderForm(self.form_data(backup_time=str(self.backup_7am.pk)))

		self.assertFalse(too_close.is_valid())
		self.assertIn('backup_time', too_close.errors)
		self.assertTrue(valid_boundary.is_valid(), valid_boundary.errors)
