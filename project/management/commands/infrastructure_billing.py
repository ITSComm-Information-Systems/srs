import csv, io
from django.core.management.base import BaseCommand

from django.conf import settings
from django.core.mail import EmailMessage
from project.pinnmodels import UmBillInputApiV
from django.db import connection

from datetime import datetime, timedelta


class Service():
    parms = None


class MiStorage(Service):
    owner_email = 'its.storage@umich.edu'
    sql = '''select a.shortcode, a."SIZE" as total_size, a.name, a.created_date, c.name as rate_name, round(c.rate * a."SIZE",2) as total_cost, d.name as owner 
            from srs_order_storageinstance a, srs_order_storagerate c, srs_oscauth_ldapgroup d 
            where  a.rate_id = c.id 
              and a.owner_id = d.id order by a.name, a.created_date'''


class Locker(Service):
    service_id = 10
    owner_email = 'arcts-storage-billing@umich.edu'
    sql = ''' select b.shortcode, b.\"SIZE\" as total_size, a.name, a.created_date, c.name as rate_name, round(c.rate * b.\"SIZE\",2) as total_cost, d.name as owner
              from srs_order_arcinstance a, srs_order_arcbilling b, srs_order_storagerate c, srs_oscauth_ldapgroup d
              where b.arc_instance_id = a.id
                and a.rate_id = c.id 
                and a.owner_id = d.id 
                and a.service_id = %s order by a.name, a.created_date '''
    parms = (service_id,)


class DataDen(Locker):
    service_id = 11
    shortcode = '123758' 

    sql = '''select b.shortcode, b.\"SIZE\" as total_size, a.amount_used, a.name, a.created_date, c.name as rate_name, 
                     case    
                      when a.research_computing_package = 1 and b.shortcode = %s and (select count(*) from srs_order_arcbilling where arc_instance_id = a.id) = 1 Then 
                        case when (a.amount_used < 1 or a.amount_used is null) then    
                            round(c.rate * 1 , 2)       
                        when a.amount_used > 10 then  
                            round(c.rate * 10 , 2)    
                        else    
                            round(c.rate * ceil(a.amount_used) ,2)     
                        end     
                      else    
                        round(c.rate * b.\"SIZE\",2)      
                      end as total_cost, d.name as owner  
                    from srs_order_arcinstance a, srs_order_arcbilling b, srs_order_storagerate c, srs_oscauth_ldapgroup d 
                    where b.arc_instance_id = a.id 
                      and a.rate_id = c.id 
                      and a.owner_id = d.id 
                      and a.service_id = %s order by a.name, a.created_date'''
    
    parms = (shortcode, service_id)


class Turbo(DataDen):
    service_id = 9
    shortcode = '123150' 
    parms = (shortcode, service_id)


class MiBackup(Service):
    owner_email = 'its.storage@umich.edu'
    sql = '''select a.shortcode, ceil(a.\"SIZE\") as total_size, a.name, to_date('20200701','YYYYMMDD') as created_date, c.name as rate_name, round(c.rate * a.\"SIZE\",2) as total_cost, d.name as owner 
            from srs_order_backupdomain a, srs_oscauth_ldapgroup d, srs_order_storagerate c 
            where  c.name = 'MB-MCOMM' 
              and a.owner_id = d.id  order by a.name  '''


class MiServer(Service):
    owner_email = 'MiServer.Support@umich.edu'
    sql = 'select a.*, a."SIZE" as total_size from srs_order_miserver_billing_v a order by name'


class MiDesktop(Service):
    owner_email = 'tbd@umich.edu'
    sql = '''
            SELECT (base.rate + (ram.rate * memory) + (cpu.rate * cpu) + (gpu.rate * gpu) + (disk.rate * d."SIZE")) * pool.quantity as total_cost
            , pool.shortcode, 'MiDesktop - Virtual Desktops' as rate_name, pool.quantity as total_size, pool.name
            , pool.created_date, (select name from srs_oscauth_ldapgroup where id = pool.owner_id) as owner
            FROM srs_services_pool pool,
            srs_services_pool_images pi,
            srs_services_imagedisk d,
            srs_services_image image
            , srs_order_storagerate base, srs_order_storagerate ram, srs_order_storagerate cpu, srs_order_storagerate disk, srs_order_storagerate gpu
            where base.name = 'MD-MIDSKTP V' and base.label = 'Base'
            and ram.name = 'MD-MIDSKTP V' and ram.label = 'Memory'
            and cpu.name = 'MD-MIDSKTP V' and cpu.label = 'CPU'
            and disk.name = 'MD-MIDSKTP V' and disk.label = 'Storage'
            and gpu.name = 'MD-MIDSKTP V' and gpu.label like 'GPU%'
            and pi.pool_id = pool.id
            and pi.image_id = image.id
            and pool.status = 'A'
            and d.image_id = image.id
        union
            select quantity * 10.0 as total_cost, shortcode, 'MiDesktop - External Desktops' as rate_name, quantity as total_size, name, created_date
            , (select name from srs_oscauth_ldapgroup where id = srs_services_pool.owner_id) as owner
            from srs_services_pool where type = 'external' and status = 'A'

        '''


class Command(BaseCommand):
    help = 'Upload Billing data for Mi-services to Pinnacle'

    def add_arguments(self, parser):
        parser.add_argument('service',type=str)

    def handle(self, *args, **options):

        service = globals()[options['service']]
        self.service = options['service']

        with connection.cursor() as cursor:
            cursor.execute(service.sql, service.parms)
            instances = self.dictfetchall(cursor)
    
        self.upload_data(instances)

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        print(cursor.description)
        
        columns = [col[0] for col in cursor.description]
        self.heading = columns
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
        csvwriter.writerow(self.heading)

        for instance in instances:
            csvwriter.writerow(instance.values())

            rec = UmBillInputApiV()
            rec.data_source = self.service #'MiStorage'
            rec.assign_date = instance['CREATED_DATE'].strftime('%m%d%Y')
            rec.unique_identifier = instance['NAME'].strip()
            rec.short_code = instance['SHORTCODE']
            rec.charge_identifier = instance['RATE_NAME']
            rec.quantity_vouchered = instance['TOTAL_SIZE']
            rec.total_amount = instance['TOTAL_COST']
            total_cost = total_cost + rec.total_amount
            rec.voucher_comment = instance['OWNER']
            rec.bill_input_file_id = today
            rec.save()
            x+=1

        print(datetime.now(), x, 'Records Loaded')
        print(datetime.now(), total_cost, 'Total Cost')

        body = f'Records Loaded: {x} \nTotal Cost: {total_cost:,}'

        print(datetime.now(), 'Load Infrastructure Billing')

        with connection.cursor() as cursor:
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

