from project.integrations import MCommunity
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from oscauth.models import AuthUserDept

import datetime

class Command(BaseCommand):
    help = 'Deactivate Users'

    def handle(self, *args, **options):

        mc = MCommunity()
        u = 0

        for user in User.objects.filter(password='').order_by('username'):   # Don't select system accounts.
            mc_user = mc.get_user(user.username)

            if not self.is_active(mc_user, user.username):

                print('    last login:', user.last_login)
                if user.is_staff:
                    print('    Staff')

                if user.is_superuser:
                    print('    Superuser')

                if user.groups.count() > 0:
                    print('    Groups:')
                    for group in user.groups.all():
                        print('     ', group)

                if user.user_permissions.count() > 0:
                    print('    Permissions:')
                    for perm in user.user_permissions.all():
                        print('     ', perm)

                department_perms = AuthUserDept.objects.filter(user=user)

                for perm in department_perms:
                    print('   ', perm.dept, perm.group)

                print(' ')

            u+=1

            #if u % 10 == 0:
            #    print(datetime.datetime.now(), str(u),'records read')
                
        print(datetime.datetime.now(), str(u),'records updated')

    def is_active(self, mc_user, username):
        if mc_user == None:
            print(username, 'not in MCommunity')
            return False
        
        for role in mc_user.umichInstRoles:
            if 'Staff' in role:
                return True

            if 'SponsoredAffiliate' in role:
                return True

            if 'Faculty' in role:
                return True

        print(username, 'Affiliations ', mc_user.umichInstRoles)
        return False

    def remove_security(self, user):

        user.groups.clear()
        user.user_permissions.clear()
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()

        department_perms = AuthUserDept.objects.filter(user=user)

        for perm in department_perms:
            print('   ', perm.dept, perm.group)
        
        #print(department_perms.count(), 'depts removed')


