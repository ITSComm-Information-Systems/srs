from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import upsert_user
from django.contrib.auth.models import User

import datetime

class Command(BaseCommand):
    help = 'Update Users from MCommunity'

    def handle(self, *args, **options):
        user_list = User.objects.all()

        u = 0

        for user in user_list:
            upsert_user(user.get_username())
            u+=1

            if u % 100 == 0:
                print(datetime.datetime.now(), str(u),'records updated')

        print(datetime.datetime.now(), str(u),'records updated')