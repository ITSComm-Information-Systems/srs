from project.integrations import MCommunity
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from oscauth.models import AuthUserDept
import csv, io, datetime

class Command(BaseCommand):
    help = 'Deactivate Users'

    def add_arguments(self, parser):
        parser.add_argument('--update')

    def handle(self, *args, **options):

        update = False
        if options['update']:
            if options['update'] == 'True':
                update = True

        mc = MCommunity()
        u = 0

        csvfile =  open(f'/Users/djamison/Downloads/user_access.csv','w', encoding='mac_roman')
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['uniqname', 'afil', 'last login','srs groups', 'srs permissions','dept permissions'])

        for user in User.objects.filter(password='').order_by('username'):   # Don't select system accounts.
            mc_user = mc.get_user(user.username)

            if not self.is_active(mc_user, user.username):

                department_perms = AuthUserDept.objects.filter(user=user)

                if mc_user == None:
                    afil = 'Not in MCommunity'
                else:
                    afil = mc_user.umichInstRoles

                csvwriter.writerow([user.username, afil, user.last_login, user.groups.count(), user.user_permissions.count(), len(department_perms)])

                if update == True:
                    department_perms.delete()
                    self.remove_security(user)

            u+=1

            if u % 10 == 0:
                print(datetime.datetime.now(), str(u),'records read')
                
        print(datetime.datetime.now(), str(u),'records updated')

    def is_active(self, mc_user, username):
        if mc_user == None:
            return False
        
        for role in mc_user.umichInstRoles:
            if 'Staff' in role:
                return True

            if 'SponsoredAffiliate' in role:
                return True

            if 'Faculty' in role:
                return True

        return False

    def remove_security(self, user):

        user.groups.clear()
        user.user_permissions.clear()
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        user.save()




