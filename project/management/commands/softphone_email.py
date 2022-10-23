from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from project.models import Email
from django.db import connections
from softphone.models import SelectionV, next_cut_date
from django.conf import settings
from django.template import Template, Context
from datetime import timedelta
import csv, io

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
        week_of = cut_date - timedelta(days = 3)

        context = {'cut_date': cut_date, 'week_of': week_of}
        email.body = Template(email.body).render(Context(context))
        email.subject = Template(email.subject).render(Context(context))

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
            user_list = self.get_ua_list(cut_date)

        if options['audit']:
            print('AUDIT ONLY****')
            for user in user_list:
                print(user)
            user_list = ['djamison']
            email.cc = 'djamison'

        self.send_email(email, user_list)

    def send_email(self, email, user_list, cc=[]):
        text_message = email.subject

        csvfile = io.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['to','cc'])

        if settings.ENVIRONMENT != 'Production':
            print('Non-prod, do not send to:', user_list)
            user_list = ['djamison']
            email.cc = 'djamison'
            email.subject = f'{settings.ENVIRONMENT} - {email.subject}'

        for user in user_list:
            if type(user)==tuple:
                to = user[0]
                cc = user[1]
            else:
                to = user

            csvwriter.writerow([to, cc])

            if to or cc:
                if to:
                    to = to + '@umich.edu'
                if cc:
                    cc = cc + '@umich.edu'

                msg = EmailMultiAlternatives(email.subject, text_message, email.sender, [to], bcc=[self.bcc], cc=[cc])
                msg.attach_alternative(email.body, "text/html")
                msg.send()

                print('Sent to', to, 'cc', cc)

        # Send Distribution List to Leads
        msg = EmailMultiAlternatives(email.subject, text_message, email.sender, [email.cc], bcc=[self.bcc])
        msg.attach_alternative(email.body, "text/html")
        msg.attach('distribution_list.csv', csvfile.getvalue(), 'text/csv')
        msg.send()

    def get_ua_list(self, cut_date):
        # For the next cut date, get a list of:
        # - Everyone that submitted an update
        # - Ambassadors for the department groups of the users
        # This is the same population that has access to the pause page.

        sql = 'select updated_by from um_softphone_selection_v where cut_date = %s ' \
        'union ' \
        'select distinct amb.uniqname ' \
        'from um_softphone_selection_v sel, ' \
        'um_mpathdw_curr_department dept, ' \
        'srs_ambassador amb ' \
        "where sel.cut_date = %s " \
        'and sel.dept_id = dept.deptid ' \
        'and dept.dept_grp = amb.dept_grp '

        user_list = []

        with connections['pinnacle'].cursor() as cursor:
            cursor.execute(sql, (cut_date.date(),cut_date.date()))
            for user in cursor.fetchall():
                user_list.append(user[0])

        return user_list