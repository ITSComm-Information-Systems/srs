import csv, io
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.core.mail import EmailMessage
from order.models import StorageInstance, ArcBilling, ArcInstance, BackupDomain
from project.pinnmodels import UmBillInputApiV
from django.db import connections, connection

from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Upload Billing data for Mi-services to Pinnacle'

    def add_arguments(self, parser):
        parser.add_argument('service',type=str)


    def handle(self, *args, **options):

        self.service = options['service']

        arc_ts_query = 'select b.shortcode, b.size, a.name, a.created_date, c.name as rate_name, round(c.rate * b.size,2) as total_cost, d.name as owner ' \
                    'from order_arcinstance a, order_arcbilling b, order_storagerate c, oscauth_ldapgroup d ' \
                    'where b.arc_instance_id = a.id ' \
                    '  and a.rate_id = c.id ' \
                    '  and a.owner_id = d.id ' 

        dataden_query = "select b.shortcode, b.size, a.amount_used, a.name, a.created_date, c.name as rate_name, " \
                    " case    " \
                    "  when a.research_computing_package = True and b.shortcode = '123758' and (select count(*) from order_arcbilling where arc_instance_id = a.id) = 1 Then " \
                    "    case when (a.amount_used < 1 or a.amount_used is null) then    " \
                    "        round(c.rate * 1 , 2)       " \
                    "    when a.amount_used > 10 then   " \
                    "        round(c.rate * 10 , 2)    " \
                    "    else    " \
                    "        round(c.rate * ceil(a.amount_used) ,2)     " \
                    "    end     " \
                    "  else    " \
                    "    round(c.rate * b.size,2)      " \
                    "  end as total_cost, d.name as owner  " \
                    "from order_arcinstance a, order_arcbilling b, order_storagerate c, oscauth_ldapgroup d " \
                    "where b.arc_instance_id = a.id " \
                    "  and a.rate_id = c.id " \
                    "  and a.owner_id = d.id " \
                    "  and a.service_id = 11 order by a.name, a.created_date "

        turbo_query = "select b.shortcode, b.size, a.amount_used, a.name, a.created_date, c.name as rate_name, " \
                    " case    " \
                    "  when a.research_computing_package = True and b.shortcode = '123150' and (select count(*) from order_arcbilling where arc_instance_id = a.id) = 1 Then " \
                    "    case when (a.amount_used < 1 or a.amount_used is null) then    " \
                    "        round(c.rate * 1 , 2)       " \
                    "    when a.amount_used > 10 then   " \
                    "        round(c.rate * 10 , 2)    " \
                    "    else    " \
                    "        round(c.rate * ceil(a.amount_used) ,2)     " \
                    "    end     " \
                    "  else    " \
                    "    round(c.rate * b.size,2)      " \
                    "  end as total_cost, d.name as owner  " \
                    "from order_arcinstance a, order_arcbilling b, order_storagerate c, oscauth_ldapgroup d " \
                    "where b.arc_instance_id = a.id " \
                    "  and a.rate_id = c.id " \
                    "  and a.owner_id = d.id " \
                    "  and a.service_id = 9 order by a.name, a.created_date "

        mistorage_query = 'select a.shortcode, a.size, a.name, a.created_date, c.name as rate_name, round(c.rate * a.size,2) as total_cost, d.name as owner ' \
                'from order_storageinstance a, order_storagerate c, oscauth_ldapgroup d ' \
                'where  a.rate_id = c.id ' \
                '  and a.owner_id = d.id order by a.name, a.created_date ' \

        mibackup_query = "select a.shortcode, ceil(a.size) as size, a.name, to_date('20200701','YYYYMMDD') as created_date, c.name as rate_name, round(c.rate * a.size,2) as total_cost, d.name as owner " \
                "from order_backupdomain a, oscauth_ldapgroup d, order_storagerate c " \
                "where  c.name = 'MB-MCOMM' " \
                "  and a.owner_id = d.id  order by a.name  "

        miserver_query = 'select * from order_miserver_billing_v order by name'

        self.owner_email = 'arcts-storage-billing@umich.edu'

        if self.service == 'MiStorage':
            sql = mistorage_query
            self.owner_email = 'its.storage@umich.edu'
        elif self.service == 'Turbo':
            sql = turbo_query
        elif self.service == 'Locker-Storage':
            sql = arc_ts_query + ' and a.service_id = 10 order by a.name, a.created_date'
        elif self.service == 'Data-Den':
            sql = dataden_query
        elif self.service == 'MiBackup':
            sql = mibackup_query
            self.owner_email = 'its.storage@umich.edu'
        elif self.service == 'MiServer':
            sql = miserver_query
            self.owner_email = 'MiServer.Support@umich.edu'
        else:
            print('Service not found')
            return

        with connection.cursor() as cursor:
            cursor.execute(sql)
            instances = self.dictfetchall(cursor)

        self.upload_data(instances)

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def upload_data(self, instances):
        print(datetime.now(), 'Upload Records')

        today = datetime.now().strftime('%m%d%Y')
        today = int(today)
        x = 0
        total_cost = 0

        csvfile = io.StringIO()
        csvwriter = csv.writer(csvfile)
        if self.service == 'MiServer':
            csvwriter.writerow(['id','cpu','created_date','os_id','os_code','managed','ad_group','shortcode','size','name','rate_name','total_cost','owner'])
        elif self.service == 'Turbo' or self.service == 'Data-Den':
            csvwriter.writerow(['shortcode','size','amount_used', 'name','date_created','rate_name','total_cost','owner'])
        else:
            csvwriter.writerow(['shortcode','size','name','date_created','rate_name','total_cost','owner'])

        for instance in instances:
            csvwriter.writerow(instance.values())

            rec = UmBillInputApiV()
            rec.data_source = self.service #'MiStorage'
            rec.assign_date = instance['created_date'].strftime('%m%d%Y')
            rec.unique_identifier = instance['name'].strip()
            rec.short_code = instance['shortcode']
            rec.charge_identifier = instance['rate_name']
            rec.quantity_vouchered = instance['size']
            rec.total_amount = instance['total_cost']
            total_cost = total_cost + rec.total_amount
            rec.voucher_comment = instance['owner']
            rec.bill_input_file_id = today
            rec.save()
            x+=1

        print(datetime.now(), x, 'Records Loaded')
        print(datetime.now(), total_cost, 'Total Cost')

        body = f'Records Loaded: {x} \nTotal Cost: {total_cost:,}'

        print(datetime.now(), 'Load Infrastructure Billing')

        with connections['pinnacle'].cursor() as cursor:
            result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21000', 'Load Infrastructure Billings'
                                   , (datetime.now() + timedelta(minutes=5)).strftime('%d-%b-%y %H:%M'),f"'{self.service}',{today}"] )
        
        print(datetime.now(), result)

        if settings.ENVIRONMENT == 'Production':
            subject = f'{self.service} Billing Records Uploaded'
            to = [self.owner_email, 'ITComBill@umich.edu', 'itscomm.information.systems@umich.edu']
        else:
            subject = f'{self.service} Billing Records Uploaded - {settings.ENVIRONMENT}'
            to = ['itscomm.information.systems@umich.edu', 'djamison@umich.edu']

        email = EmailMessage(
            subject,
            body,
            'srs-otto@umich.edu',
            to,
            []
        )

        email.attach(f'{self.service}.csv', csvfile.getvalue(), 'text/csv')

        email.send()
        print(datetime.now(), 'Process Complete')

