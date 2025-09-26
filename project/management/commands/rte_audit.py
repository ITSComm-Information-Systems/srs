from django.core.management.base import BaseCommand
from project.utils import get_query_result
from project.models import Email

import json
from django.conf import settings

class Command(BaseCommand):
    help = 'Weekly report on RTE submitters with less than 40 hours reported for prior week.'
    # This version is specific to Project Managers.
    # TDOD - lookup manager and send to other groups.

    def handle(self, *args, **options):
        print('Get Email')
        email = Email.objects.get(code='RTE_40_HOURS')
        subject = email.subject

        sql = '''
            SELECT * FROM 
            (SELECT g.WO_GROUP_LABOR_CODE as uniqname, g.WO_GROUP_NAME
            ,(SELECT sum(ACTUAL_MINS)
            FROM UM_RTE_CURRENT_TIME_ASSIGNED_V urctav
            WHERE LABOR_CODE = g.wo_group_labor_code
            and WEEK_END_DATE = (SELECT max(WEEK_END_DATE)
                                FROM UM_RTE_CURRENT_TIME_ASSIGNED_V
                                WHERE WEEK_END_DATE < sysdate)
            ) AS tot_min
            FROM UM_RTE_LABOR_GROUP_V g
            where wo_group_code = 'Network Operation'
            AND g.WO_GROUP_LABOR_CODE NOT IN ('STROUDM','JKLAAS')
            ORDER BY 3 DESC)
            WHERE tot_min IS NULL or tot_min < 2400
        '''

        for record in get_query_result(sql):
            uniqname = record['uniqname'].lower()
            print(uniqname)
            email.subject = f'{subject} - {uniqname}'
            email.to = uniqname + '@umich.edu'
            email.cc = 'stroudm@umich.edu'
            email.bcc = email.team_shared_email
            email.send()
