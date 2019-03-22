from django.db import models
from .utils import McUser
from .models import AuthUserDept
from django.contrib.auth.models import User, Group

class PinnAuthUser(models.Model):
    uniqname = models.CharField(max_length=20, primary_key=True) 
    role = models.CharField(max_length=18) 
    deptid = models.CharField(max_length=10) 
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_osc_auth_initial_load_v'

def import_users():
    user_list = PinnAuthUser.objects.all()

    for row in user_list:
        try:
            McUser(row.uniqname).add_user()
        except:
            pass

        new_record = AuthUserDept()
        new_record.user = User.objects.get(username=row.uniqname)   
        new_record.group = Group.objects.get(name=row.role)
        new_record.dept = row.deptid
        new_record.save()



