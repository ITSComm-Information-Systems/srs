from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import upsert_user
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Update Users from MCommunity'

    def handle(self, *args, **options):
        user_list = User.objects.all()

        for user in user_list:
            print('update: ', user)
            upsert_user(user.get_username())

            