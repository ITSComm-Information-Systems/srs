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
                (SELECT g.WO_GROUP_LABOR_CODE AS uniqname , g.WO_GROUP_NAME AS grp
                ,(SELECT sum(ACTUAL_MINS)
                FROM UM_RTE_CURRENT_TIME_ASSIGNED_V urctav
                WHERE LABOR_CODE = g.wo_group_labor_code
                and WEEK_END_DATE = (SELECT max(WEEK_END_DATE)
                FROM UM_RTE_CURRENT_TIME_ASSIGNED_V
                WHERE WEEK_END_DATE < sysdate)
                ) AS tot_min,
                (SELECT Labor_supervisor
                FROM workorder.LABOR_API_V
                WHERE LABOR_CODE = g.wo_group_labor_code
                AND active = 1) AS is_supervisor,
                (SELECT WO_GROUP_LABOR_CODE
                FROM UM_RTE_LABOR_GROUP_V
                WHERE WO_GROUP_LABOR_CODE IN (SELECT LABOR_CODE
                FROM workorder.LABOR_API_V
                WHERE Labor_supervisor = 1
                AND active = 1)
                AND WO_GROUP_CODE = g.wo_group_code ) AS supervisor
                FROM UM_RTE_LABOR_GROUP_V g
                where wo_group_code IN (SELECT code FROM SRS_PROJECT_CHOICE
                WHERE parent_id = (SELECT id
                FROM SRS_PROJECT_CHOICE
                WHERE code = 'RTE_40_HOURS_GROUPS'))
                )
                WHERE is_supervisor = 0
                AND (tot_min IS NULL or tot_min < 2400)
                ORDER BY grp, uniqname
        '''

        for record in get_query_result(sql):
            uniqname = record['uniqname'].lower()
            supervisor = record['supervisor'].lower()
            print(uniqname)
            email.subject = f'{subject} - {uniqname}'
            email.to = uniqname + '@umich.edu'
            email.cc = supervisor + '@umich.edu'
            email.bcc = email.team_shared_email
            email.send()
