from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from oscauth.utils import upsert_user
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User
from datetime import date

class Command(BaseCommand):
    help = 'Daily operations'

    def handle(self, *args, **options):
        print('init')

        if date.today().weekday() < 5:
            print('weekday')
            self.weekday_jobs()

        sql = '''delete from srs_auth_user_dept a
                where group_id in (5,6) -- Orderer, Reporter
                and exists (select 'x'
                from srs_auth_user_dept
                where dept = a.dept
                and user_id = a.user_id
                and group_id in (3,4) )''' # Department Manager, Proxy

        with connection.cursor() as cursor:
            cursor.execute(sql)

        sql = '''delete from srs_auth_user_dept a
                where group_id = 4  -- Proxy
                and exists (select 'x'
                from srs_auth_user_dept
                where dept = a.dept
                and user_id = a.user_id
                and group_id = 3 )''' # Manager

        with connection.cursor() as cursor:
            cursor.execute(sql)

        call_command('deptmgrupdt')

        call_command('user_deactivation', update=True)

        print('Start Group Sync')
        call_command('mc_sync')

        print('end')

    def weekday_jobs(self):
        with connection.cursor() as cursor:
            cursor.callproc('pinn_custom.um_softphone_files_k.create_sms_file_p')