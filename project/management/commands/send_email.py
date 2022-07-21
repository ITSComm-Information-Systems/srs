from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail

from pages.models import Page


class Command(BaseCommand):
    help = 'Test Email'

    def handle(self, *args, **options):
        print('start')

        #html = Page.objects.get(permalink='/restriction')
        html = Page.objects.get(permalink='test')
        #html = '<h1>SF Email</h1>'

        send_mail(
            'Subject here',
            'Here is the message.',
            'softphone@umich.edu',
            ['djamison@umich.edu'],
            fail_silently=False,
            html_message=html.bodytext
        )

        print('end')