from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from project.models import Email
from project.pinnmodels import UmMpathDwCurrDepartment
from softphone.models import Ambassador, SelectionV, next_cut_date
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Send Email to Softphone Users'
    bcc = 'itscomm.information.systems.shared.account@umich.edu'

    def add_arguments(self, parser):
        parser.add_argument('--file')  
        parser.add_argument('--email')  
        parser.add_argument('--audit')  

    def handle(self, *args, **options):

        email = Email.objects.get(code=options['email'])
        cut_date = next_cut_date()
        email.body = email.body.replace('{%%date%%}', cut_date.strftime('%B %-d, %Y'))

        user_query = SelectionV.objects.filter(cut_date=cut_date).values_list('uniqname', flat=True)
        user_list = []

        if options['file']:
            filename = options['file']
            with open(f'{filename}', encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    user_list.append(row[0])
        elif email.code in ['TUE_NO_LOGIN','WED_NO_LOGIN']:
            user_list = user_query.values_list('uniqname','updated_by').filter(zoom_login='N')
        elif email.code == 'USER_MIGRATE':
            user_list = user_query
        elif email.code == 'UA_WEEKLY':
            #TO DO ADD UA
            email.subject = email.subject.replace('{%%date%%}', cut_date.strftime('%B %-d, %Y'))

        if options['audit']:
            print('AUDIT ONLY****')
            for user in user_list:
                print(user)
            return

        self.send_email(email, user_list)

    def send_email(self, email, user_list, cc=[]):
        text_message = email.subject

        if settings.ENVIRONMENT != 'Production':
            print('Non-prod, do not send to:', user_list)
            user_list = ['djamison']

        for user in user_list:
            if type(user)==tuple:
                to = user[0]
                cc = user[1]
            else:
                to = user

            if to or cc:
                if to:
                    to = to + '@umich.edu'
                if cc:
                    cc = cc + '@umich.edu'

                msg = EmailMultiAlternatives(email.subject, text_message, email.sender, [to], bcc=[self.bcc], cc=[cc])
                msg.attach_alternative(email.body, "text/html")
                msg.send()

                print('Sent to', to, 'cc', cc)

