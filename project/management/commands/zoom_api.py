from django.core.management.base import BaseCommand

from softphone.models import Zoom, Selection, SelectionV, SubscriberCharges, next_cut_date, ZoomToken
import os, requests

import datetime, csv

class Command(BaseCommand):
    help = 'Call Zoom API to get User Data'
    BASE_URL = 'https://info.zoom.umich.edu/phoneapi/getuser/'  
    records_updated = 0
    block_size = 100

    def add_arguments(self, parser):
        parser.add_argument('--uniqname')  # Run for one user
        parser.add_argument('--start')     # Run all users starting with this one
        parser.add_argument('--file')      # Run for everyone in a file
        parser.add_argument('--cut_date')  # Run for everyone in a file
        parser.add_argument('--report')    # Report of all active zoom phones

    def handle(self, *args, **options):
        self.zoom_token = os.getenv('ZOOM_TOKEN')

        if not self.zoom_token:
            self.zoom_token = ZoomToken.objects.all()[0].token

        if options['report']:
            self.get_zoom_report()
            return
        elif options['uniqname']:
            r = self.process_user(options['uniqname'])
            print(r)
        elif options['file']:
            filename = options['file']
            with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    r = self.process_user(row[0])  
                    if r.get('elg') == False:
                        print(row[0], r['elg_code'])
                    elif not r.get('zoom'):
                        print(row[0], 'no login')
                        print(r)
        elif options['cut_date']:
            if options['cut_date'] == 'next':
                cut_date = next_cut_date()
            else:
                cut_date = options['cut_date']

            for user in SelectionV.objects.filter(uniqname__isnull=False,cut_date=cut_date,zoom_login='N').order_by('uniqname'):
                self.process_user(user.uniqname)
                if user.uniqname != user.uniqname.lower():
                    print('uniqname not all lowercase', user.uniqname)
                    sel = Selection.objects.get(subscriber=user.subscriber)
                    sel.uniqname = sel.uniqname.lower()
                    sel.save()

        elif options['start']:
            for user in SubscriberCharges.objects.filter(current_uniqname__isnull=False,current_uniqname__gt=options['start']).order_by('current_uniqname'):
                self.process_user(user.current_uniqname)        
        else:
            for user in SelectionV.objects.filter(uniqname__isnull=False).order_by('uniqname'):
                self.process_user(user.uniqname)

        print('Records Processed:', self.records_updated)


    def process_user(self, uniqname):
            
            r = requests.get( self.BASE_URL + uniqname, headers={'ZOOMAPITOKEN': self.zoom_token} )

            if not r.ok:
                print(r.status_code, r.text)

            data = r.json()

            z = Zoom()

            z.elg_code = data['elg_code']

            if data['elg']:
                z.elg = 'Y'
            else:
                z.elg = 'N'

            if data.get('zoom'):
                for key, value in data['zoom'].items():
                    if key in ('created_at','last_login_time'):
                        try:
                            value = datetime.datetime.strptime(value, "%m-%d-%Y %H:%M:%S %p %Z").date()
                        except:
                            print('login date null for user account', uniqname)

                    setattr(z, key, value)
            else:
                print('no login for', uniqname)
            
            z.id = uniqname
            z.save()

            self.records_updated = self.records_updated + 1

            if self.records_updated % self.block_size == 0:
                print(self.records_updated, 'processed, uniqname: ',uniqname)

            return data


    def get_zoom_report(self):
            url = 'https://api.zoom.us/v2/phone/users'
            params = {'page_size': 300}

            while True:
                r = requests.get( url, headers={'Authorization': f'Bearer {self.zoom_token}'}, params=params)
                data = r.json()
                if not r.ok:
                    print(r.status_code, r.text)
                    return

                for user in data['users']:
                    print(user['extension_number'], user['status'], user['email'])

                next_page_token = data.get('next_page_token')
                if next_page_token:
                    params['next_page_token'] = next_page_token
                else:
                    break

            print('total_records', data['total_records'])