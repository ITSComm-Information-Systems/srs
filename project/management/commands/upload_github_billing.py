import csv, io, requests, decimal
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django.core.mail import EmailMessage
from project.pinnmodels import UmBillInputApiV, UmOscAllActiveAcctNbrsV
from django.db import connections, connection


from datetime import datetime, timedelta

TODAY = int(datetime.now().strftime('%m%d%Y'))

class Command(BaseCommand):
    help = 'Upload Github Billing data for Mi-services to Pinnacle'

    def add_arguments(self, parser):
        parser.add_argument('--audit')

    def handle(self, *args, **options):

        print(datetime.now(), 'Upload Records')
        x = 0
        total_cost = 0

        #today = datetime.now().strftime('%m%d%Y')
        #today = int(today)

        csvfile = io.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['product','unit_type','quantity','total'])

        URL = 'https://admin.github.umich.edu/api/v1/billing/srs'
        DEV_URL = 'https://admin.beta.github.umich.edu/api/v1/billing/srs'

        r = requests.get(URL)
        data = r.json()

        if not r.ok:
            print(r.status_code, r.text)
            return

        if options.get('audit'):
            self.shortcode_audit(data)
            return

        for key, value in data['github']['shortcodes'].items():  # Loop thorugh all instances
            for line in value['line_items']:  # Loop through charges for instance (if any)
                print(line)

                rec = UmBillInputApiV()
                rec.data_source = 'GitHub'
                #rec.assign_date = instance['created_date'].strftime('%m%d%Y')
                rec.unique_identifier = key
                rec.short_code = value['shortcode']
                rec.charge_identifier = line['product']
                rec.quantity_vouchered = line['quantity']
                rec.total_amount = line['total']
                rec.voucher_comment = line['unit_type']
                rec.bill_input_file_id = TODAY
                rec.save()

                total_cost = total_cost + decimal.Decimal(rec.total_amount)
                x+=1

                csvwriter.writerow(line.values())


        print(datetime.now(), f'{x} Records Uploaded, Total Cost: {total_cost}')

        self.run_pinnacle_job()
        self.send_email(csvfile, f'Records Loaded: {x} \nTotal Cost: {total_cost}')


    def run_pinnacle_job(self):

        print(datetime.now(), 'Load GitHub Billing')

        with connections['pinnacle'].cursor() as cursor:
            result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21000', 'Load GitHub Billings'
                                   , (datetime.now() + timedelta(minutes=5)).strftime('%d-%b-%y %H:%M'),f"'GitHub',{TODAY}"] )
        
        print(datetime.now(), result)

    def shortcode_audit(self, data):
        print('Run shortcode Audit')
        for key, value in data['github']['shortcodes'].items():  # Loop thorugh all instances

            try:
                acct = UmOscAllActiveAcctNbrsV.objects.get(short_code=value['shortcode'])
            except ObjectDoesNotExist:
                print('Project:', key, 'shortcode not found:', value['shortcode'])
            

    def send_email(self, csvfile, body):

        if settings.ENVIRONMENT == 'Production':
            subject = f'GitHub Billing Records Uploaded'
            to = ['ITComBill@umich.edu', 'itscomm.information.systems@umich.edu', 'srs-github-billing@umich.edu']
        else:
            subject = f'GitHub Billing Records Uploaded - {settings.ENVIRONMENT}'
            to = ['itscomm.information.systems@umich.edu', 'djamison@umich.edu']

        email = EmailMessage(
            subject,
            body,
            'srs-otto@umich.edu',
            to,
            []
        )

        email.attach('github_billing.csv', csvfile.getvalue(), 'text/csv')

        email.send()
