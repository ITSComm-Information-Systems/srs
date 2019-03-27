from django.core.management.base import BaseCommand, CommandError

from django.db import models
from oscauth.utils import upsert_user
from oscauth.models import AuthUserDept
from django.contrib.auth.models import User, Group

class PinnDeptMgr(models.Model):
    deptid = models.CharField(max_length=10, primary_key=True) 
    dept_mgr_uniqname = models.CharField(max_length=20) 
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_current_dept_managers_v'

class Command(BaseCommand):
    help = 'Update of Department Managers'

    def handle(self, *args, **options):
        curr_mgr_list = PinnDeptMgr.objects.order_by('dept_mgr_uniqname').exclude(dept_mgr_uniqname__isnull=True).filter(dept_mgr_uniqname__startswith='a')
        curr_mgr_count = PinnDeptMgr.objects.exclude(dept_mgr_uniqname__isnull=True).count()
        distinct_users = set(curr_mgr_list)
        distinct_user_count = len(distinct_users)
        user_add_count = 0
        user_not_added_count = 0
        auth_added_count = 0
        auth_not_added_count = 0

        remove_mgr_list = AuthUserDept.objects.order_by('user', 'dept').filter(group=Group.objects.get(name='Department Manager'))
        remove_mgr_count = AuthUserDept.objects.filter(group=Group.objects.get(name='Department Manager')).count()
        auth_removed_count = 0
        auth_not_removed_count = 0

    def get_pinn_match(id,dept):
        try:
            pinn_match = PinnDeptMgr.objects.get(dept_mgr_uniqname==username) and PinnDeptMgr.objects.deptid==dept
            print('Pinnacle match found:   %s' % pinn_match)
        except:
            print('get_pinn_match threw an exception:  %s' % pinn_match)

        print('Add New Department Managers')
        print('-------------------------------------------')
    
        for row in distinct_users:
            if (User.username == row.dept_mgr_uniqname):
	            continue
            else:
                try:
#                    print("User added or updated: %s" % row.dept_mgr_uniqname)
#                    osc_user = upsert_user(row.dept_mgr_uniqname)
                    user_add_count = user_add_count + 1
                except:
                    user_not_added_count = user_not_added_count + 1
                    print('User failed MCommunity check: %s' % row.dept_mgr_uniqname)
       
        for row in curr_mgr_list:
            print('%s  %s' % (row.dept_mgr_uniqname, row.deptid))
            if (AuthUserDept.user==User.objects.get(username=row.dept_mgr_uniqname).username) and (AuthUserDept.dept==row.deptid) and (AuthUserDept.group == Group.objects.get(name='Department Manager')):
#            if (AuthUserDept.user==User.objects.get(username=row.dept_mgr_uniqname)) & (AuthUserDept.dept == row.deptid) & (AuthUserDept.group == Group.objects.get(name='Department Manager')):
	            continue
            else:
                try:
#                    print(User.objects.get(username=row.dept_mgr_uniqname).username)
#                    print('Add Security for: %s   Dept: %s' % (row.dept_mgr_uniqname, row.deptid))
#-                  osc_user = User.objects.get(username=row.dept_mgr_uniqname)
#-                  new_record = AuthUserDept()
#-                  new_record.user = osc_user  
#-                  new_record.group = Group.objects.get(name='Department Manager')
#-                  new_record.dept = row.deptid
#-                  new_record.save()
                    auth_added_count = auth_added_count + 1
                except:
                    auth_not_added_count = auth_not_added_count + 1
                    print("Unable to add Dept Manager role to AuthUserDept for User: %s  Dept: %s" % (row.dept_mgr_uniqname, row.deptid))
 
        print('-------------------------------------------')
        print('PinnDeptMgr records read: %s' % curr_mgr_count) 
        print('Distinct users read: %s' % distinct_user_count)
        print('Users added or updated: %s' % user_add_count) 
        print('Users not added: %s' % user_not_added_count) 
        print('Records added to AuthUserDept: %s' % auth_added_count) 
        print('Records not added to AuthUserDept: %s' % auth_not_added_count) 
        print('-------------------------------------------')

        print('-------------------------------------------')
        print('Remove Access for Expired Department Managers')
        print('-------------------------------------------')

        for row in remove_mgr_list:
#            print('%s' % row.user)
            #if (PinnDeptMgr.dept_mgr_uniqname==User.objects.get(username==row.user).username and PinnDeptMgr.deptid==row.dept):
#            if (row.user == PinnDeptMgr.dept_mgr_uniqname) & (row.dept == PinnDeptMgr.deptid):
            #    print('Bypass Security for: %s   Dept: %s' % (row.user, row.dept))
            #    continue
            #else:
            try:
#                pinn_match = PinnDeptMgr.objects.filter(dept_mgr_uniqname==User.objects.get(id=row.user).username and deptid==row.dept).first()
                pinn_match = get_pinn_match(row.user, row.dept)
                auth_not_removed_count = auth_not_removed_count + 1
                print("Unable to remove Dept Manager role from AuthUserDept for User: %s  Dept: %s" % (row.user, row.dept))
                    #print('Remove Security for: %s   Dept: %s' % (row.user, row.dept))
                    #auth_removed_count = auth_removed_count + 1
            except DoesNotExist:
                print('Remove Security for: %s   Dept: %s' % (row.user, row.dept))
                auth_removed_count = auth_removed_count + 1
                    #auth_not_removed_count = auth_not_removed_count + 1
                    #print("Unable to remove Dept Manager role from AuthUserDept for User: %s  Dept: %s" % (row.user, row.dept))
 
        print('-------------------------------------------')
        print('Records to be removed: %s' % remove_mgr_count) 
        print('Records removed from AuthUserDept: %s' % auth_removed_count) 
        print('Records not removed from AuthUserDept: %s' % auth_not_removed_count) 
        print('-------------------------------------------')

