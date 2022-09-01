from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from project.models import Email
from softphone.models import SelectionV, next_cut_date
import csv

class Command(BaseCommand):
    help = 'Send Email to Softphone Users'

    def add_arguments(self, parser):
        parser.add_argument('--file')  
        parser.add_argument('--email')  

    def handle(self, *args, **options):

        email = Email.objects.get(code=options['email'])
        cut_date = next_cut_date()
        body = email.body.replace('{%%date%%}', cut_date.strftime('%B %-d, %Y'))
        user_query = SelectionV.objects.filter(cut_date=cut_date).values_list('uniqname', flat=True)
        user_list = []

        if options['file']:
            filename = options['file']
            with open(f'{filename}', encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    user_list.append(row[0])
        elif email.code == 'TUE_NO_LOGIN':
            user_list = user_query.filter(zoom_login='N')
        elif email.code == 'WED_NO_LOGIN':
            user_list = user_query.filter(zoom_login='N')
        elif email.code == 'USER_MIGRATE':
            user_list = user_query
        elif email.code == 'UA_WEEKLY':
            dept_list = SelectionV.objects.filter(cut_date=cut_date).values_list('dept_id', flat=True).distinct()
            #todo UA

        for user in user_list:
            if user:
                user = user + '@umich.edu'
                send_mail(email.subject,'See attachment.', email.sender, [user], fail_silently=False, html_message=body)
                print('sent to', user)

        if email.cc:
            send_mail(email.subject,'See attachment.', email.sender, [email.cc], fail_silently=False, html_message=body)



