from django.core.management.base import BaseCommand, CommandError

from django.db import models
from oscauth.utils import upsert_user
from oscauth.models import AuthUserDept
from django.contrib.auth.models import User, Group

class PinnDeptMgr(models.Model):
    deptid = models.CharField(max_length=10) 
    dept_mgr_uniqname = models.CharField(max_length=20, primary_key=True) 
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_current_dept_managers_v'

class Command(BaseCommand):
    help = 'Update of Department Managers'

    def handle(self, *args, **options):
        curr_mgr_list = PinnDeptMgr.objects.order_by('dept_mgr_uniqname').exclude(dept_mgr_uniqname__isnull=True)  #.filter(dept_mgr_uniqname__startswith='a')
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

        print('Add New Department Managers')
        print('-------------------------------------------')
        print('  ')
        print('Adding/updating Users...')
        print('  ')
    
        for row in distinct_users:
            if (User.username == row.dept_mgr_uniqname):
	            continue
            else:
                try:
                    osc_user = upsert_user(row.dept_mgr_uniqname)
                    user_add_count = user_add_count + 1
                except:
                    user_not_added_count = user_not_added_count + 1
                    print('User failed MCommunity check: %s' % row.dept_mgr_uniqname)

        print('Adding Department Managers to AuthUserDept...')
        print('  ')

        for row in curr_mgr_list:
            try:
                pu_id = User.objects.get(username=row.dept_mgr_uniqname).id
            except User.DoesNotExist:
                pu_id = None

            try:
                pu_group = Group.objects.get(name='Department Manager').id
            except Group.DoesNotExist:
                pu_group = None

            try:
                #pu_user_group = AuthUserDept.group
                pu_user_group = AuthUserDept.objects.get(user_id=pu_id, group_id=pu_group, dept = row.deptid)
            except AuthUserDept.DoesNotExist:
                pu_user_group = None

            try:
#                pu_deptid = AuthUserDept.objects.get(dept=row.deptid).dept
                pu_deptid = AuthUserDept.objects.filter(dept=row.deptid).values('dept').distinct()
            except AuthUserDept.DoesNotExist:
                pu_deptid = None

            if pu_id is None:
                print('No User record for: %s' % row.dept_mgr_uniqname)
                auth_not_added_count = auth_not_added_count + 1
                continue
            else:
                if pu_user_group is not None and pu_deptid is not None:
#                    print('AuthUserDept record already exists for: %s  %s' % (row.dept_mgr_uniqname, row.deptid))
                    auth_not_added_count = auth_not_added_count + 1
                    continue
                else:
                    try:
                        osc_user = User.objects.get(username=row.dept_mgr_uniqname)
                        new_record = AuthUserDept()
                        new_record.user = osc_user  
                        new_record.group = Group.objects.get(name='Department Manager')
                        new_record.dept = row.deptid
                        new_record.save()
                        auth_added_count = auth_added_count + 1
#                        print("Added Dept Manager role to AuthUserDept for User: %s  Dept: %s" % (row.dept_mgr_uniqname, row.deptid))
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

            au_username = User.objects.get(username=row.user).username

            try:
                #change filter to get since the former always returns an object add dept to the criteria
                au_uniqname = PinnDeptMgr.objects.get(dept_mgr_uniqname=au_username,deptid = row.dept).values('dept_mgr_uniqname').distinct()
            except PinnDeptMgr.DoesNotExist:
                au_uniqname = None

            try:
                au_deptid = PinnDeptMgr.objects.get(deptid=row.dept).deptid
            except PinnDeptMgr.DoesNotExist:
                au_deptid = None

            if au_uniqname is None:
                print('Remove Security for: %s   Dept: %s' % (row.user, row.dept))
                AuthUserDept.objects.filter(user=row.user, dept=row.dept, group=row.group).delete()
                auth_removed_count = auth_removed_count + 1
            else:
                if au_deptid is None:
                    print('Remove Security for: %s   Dept: %s' % (row.user, row.dept))
                    AuthUserDept.objects.filter(user=row.user, dept=row.dept, group=row.group).delete()
                    auth_removed_count = auth_removed_count + 1
                else:
                    auth_not_removed_count = auth_not_removed_count + 1
                
 
        print('-------------------------------------------')
        print('Records to be removed: %s' % remove_mgr_count) 
        print('Records removed from AuthUserDept: %s' % auth_removed_count) 
        print('Records not removed from AuthUserDept: %s' % auth_not_removed_count) 
        print('-------------------------------------------')

