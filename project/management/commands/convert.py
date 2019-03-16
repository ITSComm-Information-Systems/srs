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
        distinct_users = set(user_list)

        for row in distinct_users:
            print('Add/Update User: %s' % row.uniqname)
            osc_user = upsert_user(row.uniqname)

        for row in user_list:
            try:
                print('Add Security for: %s' % row.uniqname)
                osc_user = User.objects.get(username=row.uniqname)
                new_record = AuthUserDept()
                new_record.user = osc_user  
                new_record.group = Group.objects.get(name=row.role)
                new_record.dept = row.deptid
                new_record.save()
            except:
                print("User: %s not found" % row.uniqname)


