from django.core.management.base import BaseCommand
from project.utils import get_query_result
from project.models import Email
import json


class Command(BaseCommand):
    help = 'Find expired shortcodes and send an email notice.'

    def handle(self, *args, **options):
        print('Get Email')

        email = Email.objects.get(code='SHORTCODE_ONE')

        sql = '''
                    select service, owner,
                    '[' || listagg (JSON_OBJECT (
                        KEY 'name' IS name,
                        KEY 'shortcode' IS shortcode)
                        ,',') within group (order by i.name) || ']' instances
                    from SRS_SERVICES_INSTANCES_V i
                    left join um_mpath_accts
                    on i.shortcode = um_mpath_accts.legacy_account
                    where legacy_account_status <> 'O' or legacy_account_status is null
                    group by service, owner
        '''

        for record in get_query_result(sql):
            email.context = {"service": record['service'], "instances": json.loads(record['instances'])}
            email.to = record['owner']
            email.cc = 'djamison@umich.edu,djams35@gmail.com'
            email.send()




