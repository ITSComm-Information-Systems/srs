from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create a token for given username and print to console.'

    def add_arguments(self, parser):
        parser.add_argument('--username')

    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        token = Token.objects.create(user=user)
        print(token.key)