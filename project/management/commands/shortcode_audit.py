from django.core.management.base import BaseCommand
from project.utils import get_query_result
from project.models import Email
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
                    where shortcode_status <> 'O' or shortcode_status is null
                    group by service, owner
        '''

        for record in get_query_result(sql):
            email.context = {"path": PATH, "service": record['service'], "instances": json.loads(record['instances'])}
            email.to = record['owner']
            email.reply_to = self.REPLY_TO.get(record['service'])
            email.cc = 'djamison@umich.edu,djams35@gmail.com'
            email.send()




