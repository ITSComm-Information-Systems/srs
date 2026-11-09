from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase

from order.cluster_views import (
    ClusterChangeTicketError,
    MSSQLClusterListView,
    delete_cluster_with_tickets,
)


class ClusterDeletionTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().post('/', {'operation': 'delete_cluster', 'cluster_id': '12'})
        self.request.user = SimpleNamespace(username='editor', email='editor@example.com')
        self.cluster = Mock(
            pk=12, delete_cluster_ticket_id=None, delete_primary_ticket_id=None,
            delete_secondary_ticket_id=None, primary_server_id=1, secondary_server_id=2,
        )
        self.cluster.name = 'db-td01-c'
        self.primary = Mock(in_service=True)
        self.primary.name = 'db-td01-cm1'
        self.secondary = Mock(in_service=True)
        self.secondary.name = 'db-td01-ca1'
        self.cluster.primary_server = self.primary
        self.cluster.secondary_server = self.secondary
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.mock = {}
        for name in (
            'transaction.atomic', 'get_object_or_404', 'user_cluster_queryset',
            'get_cluster_ticket_config', 'cluster_ticket_payload',
            'submit_cluster_change_ticket', 'create_ticket_server_delete',
            'Server', 'timezone',
        ):
            self.mock[name] = self.stack.enter_context(patch('order.cluster_views.' + name))
        self.mock['get_object_or_404'].return_value = self.cluster
        self.mock['cluster_ticket_payload'].return_value = {'Description': 'Cluster and disks'}
        self.mock['submit_cluster_change_ticket'].return_value = 101
        self.mock['create_ticket_server_delete'].side_effect = [
            Mock(ok=True, json=Mock(return_value={'ID': 102})),
            Mock(ok=True, json=Mock(return_value={'ID': 103})),
        ]
        self.mock['Server'].objects.select_for_update.return_value.get.side_effect = [
            self.primary, self.secondary,
        ]
        from datetime import date
        self.mock['timezone'].localdate.return_value = date(2026, 11, 9)

    def test_three_tickets_are_recorded_before_cluster_is_removed(self):
        name, ticket_ids = delete_cluster_with_tickets(12, self.request)
        self.assertEqual(name, 'db-td01-c')
        self.assertEqual(ticket_ids, [101, 102, 103])
        self.assertEqual(self.cluster.delete_primary_ticket_id, 102)
        self.assertEqual(self.cluster.delete_secondary_ticket_id, 103)
        self.assertEqual(self.cluster.save.call_count, 3)
        self.cluster.delete.assert_called_once()
        self.assertFalse(self.primary.in_service)
        self.assertFalse(self.secondary.in_service)
        self.assertEqual(self.primary.name, 'db-td01-cm1-Ended-20261109')
        retirement_calls = self.mock['create_ticket_server_delete'].call_args_list
        self.assertIs(retirement_calls[0].args[0], self.primary)
        self.assertIs(retirement_calls[1].args[0], self.secondary)
        self.assertIn('101', retirement_calls[0].args[2])

    def test_server_ticket_failure_preserves_cluster_and_prior_progress(self):
        self.mock['create_ticket_server_delete'].side_effect = [
            Mock(ok=True, json=Mock(return_value={'ID': 102})),
            Mock(ok=False, status_code=500),
        ]
        with self.assertRaises(ClusterChangeTicketError):
            delete_cluster_with_tickets(12, self.request)
        self.assertEqual(self.cluster.delete_cluster_ticket_id, 101)
        self.assertEqual(self.cluster.delete_primary_ticket_id, 102)
        self.assertIsNone(self.cluster.delete_secondary_ticket_id)
        self.cluster.delete.assert_not_called()
        self.primary.save.assert_not_called()
        self.secondary.save.assert_not_called()

    def test_retry_skips_confirmed_tickets(self):
        self.cluster.delete_cluster_ticket_id = 101
        self.cluster.delete_primary_ticket_id = 102
        self.mock['create_ticket_server_delete'].side_effect = [
            Mock(ok=True, json=Mock(return_value={'ID': 103})),
        ]
        delete_cluster_with_tickets(12, self.request)
        self.mock['submit_cluster_change_ticket'].assert_not_called()
        self.mock['create_ticket_server_delete'].assert_called_once()
        self.assertIs(self.mock['create_ticket_server_delete'].call_args.args[0], self.secondary)

    def test_unconfirmed_cluster_ticket_prevents_retirement(self):
        self.mock['submit_cluster_change_ticket'].side_effect = ClusterChangeTicketError()
        with self.assertRaises(ClusterChangeTicketError):
            delete_cluster_with_tickets(12, self.request)
        self.mock['create_ticket_server_delete'].assert_not_called()
        self.cluster.delete.assert_not_called()

    def test_missing_ticket_id_prevents_retirement(self):
        self.mock['create_ticket_server_delete'].side_effect = [
            Mock(ok=True, json=Mock(return_value={})),
        ]
        with self.assertRaises(KeyError):
            delete_cluster_with_tickets(12, self.request)
        self.cluster.delete.assert_not_called()


class ClusterDeleteViewTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().post('/', {'operation': 'delete_cluster', 'cluster_id': '12'})
        self.request.user = SimpleNamespace(username='editor')

    @patch('order.cluster_views.is_mssql_dba', return_value=False)
    def test_non_dba_is_forbidden(self, authorized):
        self.assertEqual(MSSQLClusterListView.as_view()(self.request).status_code, 403)

    @patch('order.cluster_views.user_cluster_queryset')
    @patch('order.cluster_views.get_object_or_404', side_effect=Http404)
    @patch('order.cluster_views.delete_cluster_with_tickets')
    def test_unowned_cluster_cannot_be_deleted(self, delete, get_cluster, queryset):
        with self.assertRaises(Http404):
            MSSQLClusterListView().post(self.request)
        delete.assert_not_called()

    @patch('order.cluster_views.logger')
    @patch('order.cluster_views.render')
    @patch('order.cluster_views.user_cluster_queryset')
    @patch('order.cluster_views.get_object_or_404', return_value=Mock(pk=12))
    @patch('order.cluster_views.delete_cluster_with_tickets', side_effect=TimeoutError)
    def test_failure_retains_cluster_and_shows_retry_warning(self, delete, get_cluster, queryset, render, logger):
        MSSQLClusterListView().post(self.request)
        self.assertEqual(render.call_args.kwargs['status'], 502)
        self.assertIn('Check TDX', render.call_args.args[2]['error_message'])
        self.assertEqual(queryset.return_value.filter.return_value.update.call_args.kwargs['ticket_status'], 'delete_failed')