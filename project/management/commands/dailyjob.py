from django.db import connection
from django.core.management.base import BaseCommand, CommandError
<<<<<<< HEAD
=======
from django.core.management import call_command
>>>>>>> 6bda00dc59214388fe2575f626f3134fb1f372f7

from oscauth.utils import upsert_user
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Daily operations'

    def handle(self, *args, **options):
        print('init')

        sql = '''delete from auth_user_dept a
                where group_id in (5,6) -- Orderer, Reporter
                and exists (select 'x'
                from auth_user_dept
                where dept = a.dept
                and user_id = a.user_id
                and group_id in (3,4) )''' # Department Manager, Proxy

        with connection.cursor() as cursor:
            cursor.execute(sql)

        sql = '''delete from auth_user_dept a
                where group_id = 4  -- Proxy
                and exists (select 'x'
                from auth_user_dept
                where dept = a.dept
                and user_id = a.user_id
                and group_id = 3 )''' # Manager

        with connection.cursor() as cursor:
            cursor.execute(sql)
<<<<<<< HEAD
=======

        call_command('deptmgrupdt')
>>>>>>> 6bda00dc59214388fe2575f626f3134fb1f372f7
        
        print('end')
