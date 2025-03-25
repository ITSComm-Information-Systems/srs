from django.core.management.base import BaseCommand
from django.utils import timezone
from softphone.models import Zoom, Selection, SelectionV, SubscriberCharges, next_cut_date, ZoomToken, ZoomAPI
import os, requests, time

import datetime, csv

FLINT = 'iWZlFMvWREiQ2Jblp6k1LQ'
AA = 'KTy52PDyS9CzCCb29Qf5tg'
DEARBORN =  'gIcx3ptyTT6Xdnac0azKBg'
DEFAULT_ADDRESS = [FLINT, AA, DEARBORN]
ZOOM_URL = 'https://api.zoom.us/v2/phone/users'

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
        parser.add_argument('--e911')      # Update e911 Data

    def handle(self, *args, **options):
        self.zoom_token = os.getenv('ZOOM_TOKEN')

        if not self.zoom_token:
            self.zoom_token = ZoomToken.objects.all()[0].token

        if options['report']:
            self.get_zoom_report()
            return
        elif options['e911']:
            self.update_e911(options['e911'])
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
            params = {'page_size': 300}
            all_users = []

            while True:
                r = requests.get( ZOOM_URL, headers={'Authorization': f'Bearer {self.zoom_token}'}, params=params)
                data = r.json()
                if not r.ok:
                    print(r.status_code, r.text)
                    return

                for user in data['users']:
                    all_users.append(user['id'])
                    print(user['extension_number'], user['status'], user['email'])

                next_page_token = data.get('next_page_token')
                if next_page_token:
                    params['next_page_token'] = next_page_token
                else:
                    break

            print('total_records', data['total_records'])
            return all_users


    def update_e911(self, parameter):
        x = 0

        if parameter == 'new':  # New Users
            all_users = self.get_zoom_report()
            imported_users = list(ZoomAPI.objects.values_list('id', flat=True))
            user_list = list(set(all_users) - set(imported_users))
        elif parameter == 'missing':   # Check All Users Missing Emergency Addresses
            user_list = list(ZoomAPI.objects.values_list('id', flat=True).filter(address_updated=False))
        else:  # All Active Users
            user_list = self.get_zoom_report()

        for user in user_list:
            x +=1

            r = requests.get(f'{ZOOM_URL}/{user}', headers={'Authorization': f'Bearer {self.zoom_token}'})
            data = r.json()
            if not r.ok:
                print(r.status_code, r.text)
                if r.status_code == 401 and r.text == '{"code":124,"message":"Access token has expired."}':
                    time.sleep(10)
                    self.zoom_token = ZoomToken.objects.all()[0].token
                    continue

            print(x, data['extension_number'], data['status'], data['email'])

            zoom = ZoomAPI()
            zoom.id = user
            zoom.phone_number = data['extension_number']
            zoom.username = data['email'].split('@')[0]
            zoom.default_address = data['emergency_address']['id'] in DEFAULT_ADDRESS  # Flag if address has been changed from the default
            zoom.last_updated = timezone.now()
            zoom.save()

        print('end process', timezone.now())