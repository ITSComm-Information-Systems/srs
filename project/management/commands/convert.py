from django.core.management.base import BaseCommand, CommandError

from django.db import models
from oscauth.utils import upsert_user
from oscauth.models import AuthUserDept
from django.contrib.auth.models import User, Group

class PinnAuthUser(models.Model):
    uniqname = models.CharField(max_length=20, primary_key=True) 
    role = models.CharField(max_length=18) 
    deptid = models.CharField(max_length=10) 
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_osc_auth_initial_load_v'

class Command(BaseCommand):
    help = 'Initial Conversion'

    def handle(self, *args, **options):
        user_list = PinnAuthUser.objects.order_by('uniqname')
        user_count = PinnAuthUser.objects.count()
        distinct_users = set(user_list)
        distinct_user_count = len(distinct_users)
        user_add_count = 0
        user_not_added_count = 0
        auth_added_count = 0
        auth_not_added_count = 0

        for row in distinct_users:
            try:
#                print('Add/Update User: %s' % row.uniqname)
                osc_user = upsert_user(row.uniqname)
                user_add_count = user_add_count + 1
            except:
                user_not_added_count = user_not_added_count + 1
                print('User failed MCommunity check: %s' % row.uniqname)
       
        for row in user_list:
            try:
                print('Add Security for: %s' % row.uniqname)
                osc_user = User.objects.get(username=row.uniqname)
                new_record = AuthUserDept()
                new_record.user = osc_user  
                new_record.group = Group.objects.get(name=row.role)
                new_record.dept = row.deptid
                new_record.save()
                auth_added_count = auth_added_count + 1
            except:
                auth_not_added_count = auth_not_added_count + 1
                print("Unable to add AuthUserDept for User: %s  Role: %s  Dept: %s" % (row.uniqname, row.role, row.deptid))
 
        print('-------------------------------------------')
        print('PinnAuthUser records read: %s' % user_count) 
        print('Distinct users read: %s' % distinct_user_count)
        print('Users added or updated: %s' % user_add_count) 
        print('Users not added: %s' % user_not_added_count) 
        print('Records added to AuthUserDept: %s' % auth_added_count) 
        print('Records not added to AuthUserDept: %s' % auth_not_added_count) 
        print('-------------------------------------------')
 
