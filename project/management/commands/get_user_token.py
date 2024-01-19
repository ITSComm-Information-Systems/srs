from django.core.management.base import BaseCommand, CommandError

from django.db import models
from oscauth.utils import upsert_user
from oscauth.models import AuthUserDept
from django.contrib.auth.models import User, Group



from rest_framework.authtoken.models import Token





class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('--username')


    def handle(self, *args, **options):

        user = User.objects.get(username=options['username'])
        token = Token.objects.create(user=user)
        print(token.key)