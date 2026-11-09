from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase

from order.cluster_views import (
    ClusterChangeTicketError,
    MSSQLClusterManageView,
    cluster_ticket_payload,
    submit_cluster_change_ticket,
)


class ClusterChangeTicketTests(SimpleTestCase):
    def setUp(self):
        self.config = dict(FormID=1, TypeID=2, ServiceID=3, ResponsibleGroupID=4)
        self.request = RequestFactory().post('/', {'operation': 'save'})
        self.request.user = SimpleNamespace(username='editor', email='editor@example.com')
        self.cluster = Mock(pk=12, cluster_ticket_id=100)
        self.cluster.name = 'db-td01-c'

    @patch('order.cluster_views.TDx')
    @patch('order.cluster_views.cluster_ticket_payload')
    def test_change_ticket_reuses_routing_and_identifies_editor(self, payload, tdx):
        payload.return_value = dict(self.config, RequestorEmail='creator@example.com')
        tdx.return_value.create_ticket.return_value.json.return_value = {'ID': 123}
        ticket_id = submit_cluster_change_ticket(
            self.cluster, self.request, self.config, 'Update disk', 'Size: 10', 'Size: 20',
        )
        submitted = tdx.return_value.create_ticket.call_args.args[0]
        for key, value in self.config.items():
            self.assertEqual(submitted[key], value)
        self.assertEqual(submitted['RequestorEmail'], 'editor@example.com')
        self.assertIn('Update disk', submitted['Title'])
        self.assertIn('Before:\nSize: 10', submitted['Description'])
        self.assertIn('After:\nSize: 20', submitted['Description'])
        self.assertIn('Original cluster ticket: 100', submitted['Description'])
        self.assertEqual(ticket_id, 123)

    @patch('order.cluster_views.logger')
    @patch('order.cluster_views.TDx')
    @patch('order.cluster_views.cluster_ticket_payload', return_value={})
    def test_ticket_rejections_timeouts_and_invalid_responses_fail(self, payload, tdx, logger):
        for response, error in (
            (Mock(ok=False, status_code=500), None),
            (None, TimeoutError()),
            (Mock(ok=True, json=Mock(return_value={})), None),
        ):
            with self.subTest(error=error, response=response):
                tdx.return_value.create_ticket.side_effect = error
                tdx.return_value.create_ticket.return_value = response
                with self.assertRaises(ClusterChangeTicketError):
                    submit_cluster_change_ticket(
                        self.cluster, self.request, self.config, 'Remove disk', 'Disk', 'None',
                    )

    def test_snapshot_includes_every_editable_configuration_field(self):
        self.cluster.regulated_data.all.return_value = [SimpleNamespace(pk=1, label='FERPA')]
        self.cluster.non_regulated_data.all.return_value = []
        self.cluster.disks.all.return_value = []
        self.cluster.shortcode = '123456'
        description = cluster_ticket_payload(self.cluster, self.request, self.config)['Description']
        self.assertIn('Shortcode: 123456', description)
        self.assertIn('FERPA', description)
        self.assertIn('Regulated data:', description)
        self.assertIn('Non-regulated data:', description)


class ClusterChangeDispatchTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().post('/', {'operation': 'edit_cluster'})
        self.request.user = SimpleNamespace(username='editor', email='editor@example.com')
        self.cluster = Mock(pk=12)
        self.view = MSSQLClusterManageView()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.mock = {}
        for name in (
            'get_object_or_404', 'user_cluster_queryset', 'get_cluster_ticket_config',
            'cluster_ticket_payload', 'submit_cluster_change_ticket', 'render',
            'MSSQLClusterDiskForm', 'MSSQLClusterEditForm', 'transaction.atomic',
        ):
            self.mock[name] = self.stack.enter_context(patch('order.cluster_views.' + name))
        self.mock['get_object_or_404'].return_value = self.cluster
        self.mock['user_cluster_queryset'].return_value.select_for_update.return_value.get.return_value = self.cluster
        self.mock['cluster_ticket_payload'].side_effect = [
            {'Description': 'Before'}, {'Description': 'After'},
        ]
        self.mock['submit_cluster_change_ticket'].return_value = 456
        self.handler = self.stack.enter_context(patch.object(self.view, 'process_change'))

    def test_all_edit_operations_dispatch_a_change_ticket(self):
        for operation in ('edit_cluster', 'add', 'save', 'remove'):
            with self.subTest(operation=operation):
                self.request.POST = {'operation': operation}
                self.mock['cluster_ticket_payload'].side_effect = [
                    {'Description': 'Before'}, {'Description': 'After'},
                ]
                self.mock['submit_cluster_change_ticket'].reset_mock()
                self.view.post(self.request, 12)
                self.mock['submit_cluster_change_ticket'].assert_called_once()
                context = self.mock['render'].call_args.args[2]
                self.assertIn('TDX ticket 456', context['notice'])

    def test_unchanged_or_invalid_submissions_do_not_dispatch(self):
        self.mock['cluster_ticket_payload'].side_effect = [
            {'Description': 'Same'}, {'Description': 'Same'},
        ]
        self.assertIs(self.view.post(self.request, 12), self.handler.return_value)
        self.mock['submit_cluster_change_ticket'].assert_not_called()

    def test_ticket_failure_exits_transaction_with_exception(self):
        self.mock['submit_cluster_change_ticket'].side_effect = ClusterChangeTicketError()
        self.view.post(self.request, 12)
        transaction_exit = self.mock['transaction.atomic'].return_value.__exit__
        self.assertIs(transaction_exit.call_args.args[0], ClusterChangeTicketError)
        context = self.mock['render'].call_args.args[2]
        self.assertIn('not saved', context['error_message'])
        self.assertNotIn('notice', context)

    def test_missing_routing_does_not_mutate_records(self):
        self.mock['get_cluster_ticket_config'].side_effect = ImproperlyConfigured()
        self.view.post(self.request, 12)
        self.handler.assert_not_called()

    def test_retry_uses_original_creation_retry_path(self):
        self.request.POST = {'operation': 'retry_tickets'}
        self.view.post(self.request, 12)
        self.handler.assert_called_once_with(self.request, self.cluster)
        self.mock['submit_cluster_change_ticket'].assert_not_called()