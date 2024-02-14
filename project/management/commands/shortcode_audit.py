from django.core.management.base import BaseCommand
from project.utils import get_query_result
from project.models import Email
from project.integrations import Slack, MCommunity

import json
from django.conf import settings

class Command(BaseCommand):
    help = 'Find expired shortcodes and send an email notice.'

    REPLY_TO = {
        'MiStorage': 'ITS.storage@umich.edu',
        'MiBackup': 'ITS.storage@umich.edu',
        'Turbo Research Storage': 'arcts-storage-billing@umich.edu',
        'Locker Storage': 'arcts-storage-billing@umich.edu',
        'Data Den': 'arcts-storage-billing@umich.edu',
        'MiServer': 'MiServer.support@umich.edu',
        'MiDatabase': '',
        'MiDesktop': 'midesktop.support@umich.edu',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",  # Set to true if present.
            help="Ignore Quantity Warning",
        )


    def handle(self, *args, **options):
        print('Get Email')

        PATH = settings.SITE_URL + '/orders/wf/'

        email = Email.objects.get(code='SHORTCODE_ONE')

        sql = '''
                    select service, owner,
                    '[' || listagg (JSON_OBJECT (
                        KEY 'wf' IS workflow_id,
                        KEY 'name' IS name,
                        KEY 'shortcode' IS shortcode)
                        ,',') within group (order by i.name) || ']' instances
                    from SRS_SERVICES_INSTANCES_V i
                    where service <> 'MiDatabase'
                    and (shortcode_status <> 'O' or shortcode_status is null)
                    group by service, owner
        '''

        record_list = get_query_result(sql)

        if len(record_list) > 10:  
            msg = f'ERROR: Shortcode Audit {len(record_list)} Records Found.'
            Slack(msg)
            if not options['force']: 
                print('abort')
                return

        mc = MCommunity()

        for record in record_list:
            if not record['owner']:
                Slack('Shortcode Audit, no owner found')
                continue
                
            to = mc.get_group_email(record['owner'])

            if to:
                email.context = {"path": PATH, "service": record['service'], "instances": json.loads(record['instances'])}
                email.to = to
                email.reply_to = self.REPLY_TO.get(record['service'])
                email.cc = self.REPLY_TO.get(record['service'])
                email.bcc = email.team_shared_email
                email.send()
            else:
                Slack('Shortcode Audit, no email found')




            to = mc.get_group_email(record['owner'])

            if to:
                email.context = {"path": PATH, "service": record['service'], "instances": json.loads(record['instances'])}
                email.to = to
                email.reply_to = self.REPLY_TO.get(record['service'])
                email.cc = self.REPLY_TO.get(record['service'])
                email.bcc = email.team_shared_email
                email.send()
            else:
                Slack().send_message('Shortcode Audit, no email found', 'srs-errors')
