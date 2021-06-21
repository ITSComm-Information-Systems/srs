from django.core.management.base import BaseCommand, CommandError
from django.core import management

from oscauth.models import AuthUserDept
from project.pinnmodels import UmOscAuthUsersApi


class Command(BaseCommand):
    help = 'Initial Load for UM_OSC_AUTH_USERS_API_V'

    def handle(self, *args, **options):
        print('Start Load')

        auth_list = AuthUserDept.objects.all().select_related('user','group')

        for auth in auth_list:
            rec = UmOscAuthUsersApi()
            rec.dept = auth.dept
            rec.group_name = auth.group
            rec.username = auth.user
            rec.save()
