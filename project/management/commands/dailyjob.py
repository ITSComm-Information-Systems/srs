from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from oscauth.utils import upsert_user
from oscauth.models import LDAPGroup
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Daily operations'

    def handle(self, *args, **options):
        print('init')

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

        # Update LDAP Group membership used by storage, etc.
        for group in LDAPGroup.objects.order_by('name'):
            group.update_membership()

        print('end')
