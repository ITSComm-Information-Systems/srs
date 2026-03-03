import csv, io
from django.core.management.base import BaseCommand

from django.conf import settings
from django.core.mail import EmailMessage
from project.pinnmodels import UmBillInputApiV
from django.db import connection

from datetime import datetime, timedelta


class ServiceBilling():
    help = 'Upload Billing data for Mi-services to Pinnacle'
    heading = ['shortcode','size','name','date_created','rate_name','total_cost','owner']

    def __init__(self):
        today = datetime.now().strftime('%m%d%Y')
        self.today = int(today)
        self.service = self.__class__.__name__

    def get_records(self):
        with connection.cursor() as cursor:
            cursor.execute(self.sql)
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

        x = 0
        total_cost = 0

        self.csvfile = io.StringIO()
        csvwriter = csv.writer(self.csvfile)
        csvwriter.writerow(self.heading)

        for instance in instances:
            csvwriter.writerow(instance.values())

            rec = UmBillInputApiV()
            rec.data_source = self.__class__.__name__ #'MiStorage'
            rec.assign_date = instance['CREATED_DATE'].strftime('%m%d%Y')
            rec.unique_identifier = instance['NAME'].strip()
            rec.short_code = instance['SHORTCODE']
            rec.charge_identifier = instance['RATE_NAME']
            rec.quantity_vouchered = instance['TOTAL_SIZE']
            rec.total_amount = instance['TOTAL_COST']
            total_cost = total_cost + rec.total_amount
            rec.voucher_comment = instance['OWNER']
            rec.bill_input_file_id = self.today
            rec.save()
            x+=1

        print(datetime.now(), x, 'Records Loaded')
        print(datetime.now(), total_cost, 'Total Cost')

        self.body = f'Records Loaded: {x} \nTotal Cost: {total_cost:,}'


    def run_pinnacle_job(self):
        print(datetime.now(), 'Load Infrastructure Billing')

        with connection.cursor() as cursor:
            result = cursor.callproc('pinn_custom.um_util_k.um_scheduler_p',  ['JOBID21000', 'Load Infrastructure Billings'
                                   , (datetime.now() + timedelta(minutes=5)).strftime('%d-%b-%y %H:%M'),f"'{self.service}',{self.today}"] )
        
        print(datetime.now(), result)


    def send_email(self):

        if settings.ENVIRONMENT == 'Production':
            subject = f'{self.service} Billing Records Uploaded'
            to = [self.owner_email, 'ITComBill@umich.edu', 'itscomm.information.systems@umich.edu']
        else:
            subject = f'{self.service} Billing Records Uploaded - {settings.ENVIRONMENT}'
            to = ['itscomm.information.systems@umich.edu', 'djamison@umich.edu']

        email = EmailMessage(
            subject,
            self.body,
            'srs-otto@umich.edu',
            to,
            []
        )

        email.attach(f'{self.service}.csv', self.csvfile.getvalue(), 'text/csv')

        email.send()
        

class MiDesktop(ServiceBilling):
    owner_email = 'midesktop.support@umich.edu'
    heading = ['shortcode','size','name','date_created','rate_name','total_cost','voucher_comment']
    sql = '''
            select shortcode,quantity as "TOTAL_SIZE",name,CREATED_DATE,'MD-MIDSKTP V' as rate_name,
            (case when "TYPE" = 'external' then quantity * 10
                else quantity*image_cost end) as total_cost
            ,voucher as owner
            from (
            select pool.created_date, pool.name, shortcode, quantity, max(image.total) as image_cost, pool.owner_id,
            (case when "TYPE" = 'external' then 'External Desktops' else 
            sum(memory) || ' GB;' || sum(cpu) || ' CPU;' || sum(storage) || ' GB;' end) as voucher, pool."TYPE"
            from srs_services_pool pool  -- 43
            left join srs_services_pool_images pi
            on pi.pool_id = pool.id
            left join srs_services_image_cost_v image
            on pi.image_id = image.id
            where pool.status = 'A'
            group by pool.name, shortcode, quantity, pool.created_date, pool.owner_id, pool."TYPE"
            ) 
            order by name
        '''


class Locker(ServiceBilling):
    owner_email = 'arcts-storage-billing@umich.edu'
    sql = 'select b.shortcode, b.\"SIZE\" as total_size, a.name, a.created_date, c.name as rate_name, round(c.rate * b.\"SIZE\",2) as total_cost, d.name as owner ' \
                    'from srs_order_arcinstance a, srs_order_arcbilling b, srs_order_storagerate c, srs_oscauth_ldapgroup d ' \
                    'where b.arc_instance_id = a.id ' \
                    '  and a.rate_id = c.id ' \
                    '  and a.owner_id = d.id ' \
                     ' and a.service_id = 10 order by a.name, a.created_date'


class DataDen(ServiceBilling):
    heading = ['shortcode','size','amount_used', 'name','date_created','rate_name','total_cost','owner']
    sql = "select b.shortcode, b.\"SIZE\" as total_size, a.amount_used, a.name, a.created_date, c.name as rate_name, " \
                    " case    " \
                    "  when a.research_computing_package = 1 and b.shortcode = '123758' and (select count(*) from srs_order_arcbilling where arc_instance_id = a.id) = 1 Then " \
                    "    case when (a.amount_used < 1 or a.amount_used is null) then    " \
                    "        round(c.rate * 1 , 2)       " \
                    "    when a.amount_used > 10 then   " \
                    "        round(c.rate * 10 , 2)    " \
                    "    else    " \
                    "        round(c.rate * ceil(a.amount_used) ,2)     " \
                    "    end     " \
                    "  else    " \
                    "    round(c.rate * b.\"SIZE\",2)      " \
                    "  end as total_cost, d.name as owner  " \
                    "from srs_order_arcinstance a, srs_order_arcbilling b, srs_order_storagerate c, srs_oscauth_ldapgroup d " \
                    "where b.arc_instance_id = a.id " \
                    "  and a.rate_id = c.id " \
                    "  and a.owner_id = d.id " \
                    "  and a.service_id = 11 order by a.name, a.created_date "


class Turbo(ServiceBilling):
    heading = ['shortcode','size','amount_used', 'name','date_created','rate_name','total_cost','owner']
    sql = "select b.shortcode, b.\"SIZE\" as total_size, a.amount_used, a.name, a.created_date, c.name as rate_name, " \
                    " case    " \
                    "  when a.research_computing_package = 1 and b.shortcode = '123150' and (select count(*) from srs_order_arcbilling where arc_instance_id = a.id) = 1 Then " \
                    "    case when (a.amount_used < 1 or a.amount_used is null) then    " \
                    "        round(c.rate * 1 , 2)       " \
                    "    when a.amount_used > 10 then   " \
                    "        round(c.rate * 10 , 2)    " \
                    "    else    " \
                    "        round(c.rate * ceil(a.amount_used) ,2)     " \
                    "    end     " \
                    "  else    " \
                    "    round(c.rate * b.\"SIZE\", 2)      " \
                    "  end as total_cost, d.name as owner  " \
                    "from srs_order_arcinstance a, srs_order_arcbilling b, srs_order_storagerate c, srs_oscauth_ldapgroup d " \
                    "where b.arc_instance_id = a.id " \
                    "  and a.rate_id = c.id " \
                    "  and a.owner_id = d.id " \
                    "  and a.service_id = 9 order by a.name, a.created_date "


class MiStorage(ServiceBilling):
    sql = 'select a.shortcode, a."SIZE" as total_size, a.name, a.created_date, c.name as rate_name, round(c.rate * a."SIZE",2) as total_cost, d.name as owner ' \
                'from srs_order_storageinstance a, srs_order_storagerate c, srs_oscauth_ldapgroup d ' \
                'where  a.rate_id = c.id ' \
                '  and a.owner_id = d.id order by a.name, a.created_date ' \


class MiBackup(ServiceBilling):
    sql = "select a.shortcode, ceil(a.\"SIZE\") as total_size, a.name, to_date('20200701','YYYYMMDD') as created_date, c.name as rate_name, round(c.rate * a.\"SIZE\",2) as total_cost, d.name as owner " \
                "from srs_order_backupdomain a, srs_oscauth_ldapgroup d, srs_order_storagerate c " \
                "where  c.name = 'MB-MCOMM' " \
                "  and a.owner_id = d.id  order by a.name  "


class MiServer(ServiceBilling):
    sql = 'select a.*, a."SIZE" as total_size from srs_order_miserver_billing_v a order by name'


class Container(ServiceBilling):
    sql = 'select 1 from dual;'   # TODO create procs when we get the test file.

    def get_records(self):
        print('foo')

    def run_pinnacle_job(self):
        print('bar')

    def send_email(self):
        print('baz')


class Command(BaseCommand):
    help = 'Upload Billing data for Mi-services to Pinnacle'

    def add_arguments(self, parser):
        parser.add_argument('service',type=str)

    def handle(self, *args, **options):
        from . import upload_billing as this
        billing = getattr(this, options['service'])()    # Instantiate me sometime when you have no class.
        billing.get_records()
        billing.run_pinnacle_job()
        billing.send_email()
        print(datetime.now(), 'Process Complete')

