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
            'Your U-M phone number is scheduled to transition to U-M Zoom Phone on Thursday',
            'See attachment.',
            'Testy McTestface',
            ['djamison@umich.edu','jwalfish@umich.edu'],
            fail_silently=False,
            html_message=html.bodytext
        )

        print('end')