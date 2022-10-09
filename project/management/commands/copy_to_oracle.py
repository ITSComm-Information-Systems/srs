from dataclasses import field
from tempfile import TemporaryFile
from order import models as ord
from oscauth import models as oa
from django.db import connections
from django.core.management.base import BaseCommand
from project import models as pj
from pages.models import Page
from django.contrib.auth import models as am
#from order import models as om

source_database = 'srsqa'
target_database = 'pinnqa'


AUTH = [#am.User, am.Group, am.Permission,
        'auth_group_permissions', 'auth_user_user_permissions', 'auth_user_groups']

OSCAUTH = [ oa.LDAPGroup, oa.LDAPGroupMember, oa.AuthUserDept, oa.Role, oa.Grantor, oa.AuthUserDept]

PROJECT = [ pj.Choice, Page,
            pj.ActionLog, pj.Email, pj.Webhooks ]

ORDER = [   #ord.Chartcom
            #, ord.ServiceGroup, ord.Service
            #, ord.ProductCategory, ord.Product
            #, ord.Action, ord.Step, 'order_action_steps', ord.Element, ord.Constant
            #, ord.Order, ord.Item
             ord.ChargeType, 'order_action_charge_types'
            , ord.FeatureType, ord.FeatureCategory, ord.Feature, 'order_feature_category'
            , ord.Restriction, 'order_restriction_category'
            , ord.BackupDomain, ord.BackupNode
            , ord.StorageRate, ord.StorageOwner, ord.StorageMember, ord.StorageInstance, ord.StorageHost
            , ord.ArcInstance, ord.ArcBilling, ord.ArcHost
            , ord.Server, ord.ServerDisk
        ]

#ORDER = [ ord.Restriction, 'order_restriction_category' ]
TEST = [ 'auth_user_user_permissions' ]

APPS = [TEST]


class Command(BaseCommand):
    help = 'Copy data from postgres to Oracle'

    def add_arguments(self, parser):
        parser.add_argument('--nobulk')

    def handle(self, *args, **options):
        if options['nobulk']:
            #model = globals().options['nobulk']
            #model = globals()[options['nobulk']]()
            #print(options['nobulk'], 'parm')
            self.bulk_cursor(ord.Item, bulk=False)
            return

        for app in APPS:
            self.truncate_tables(app)

            for model in app:
                #self.copy_table(model)
                self.bulk_cursor(model)

    
    def copy_table(self, model):
        target_name = 'SRS_' + model._meta.db_table
        print('copy to', target_name)

        for source in model.objects.all().order_by('id'):
            target = source
            target._meta.db_table = target_name

            target.save(using='pinnacle', force_insert=True)


    def truncate_tables(self, model_list):
        #cursor = connections['pinnacle'].cursor()
        with connections[target_database].cursor() as cursor:
            for model in reversed(model_list):
                if isinstance(model, str):
                    target_name = f'SRS_{ model }'
                else:
                    target_name = 'SRS_' + model._meta.db_table

                print('truncate', target_name)
                cursor.execute(f'truncate table {target_name}')

        #cursor.close()

    def bulk_cursor(self, model, bulk=True):
        if isinstance(model, str):
            source = model
            target = f'SRS_{ model }'
            field_count = 2
            select_fields = '*'
            insert_fields = ''
        else:
            source = model._meta.db_table
            target = 'SRS_' + model._meta.db_table
            field_count = len(model._meta.fields) - 1

            fields = ''
            select_fields = ''

            for field in model._meta.fields:
                select_fields = select_fields + '"' + field.column + '", '
                fields = fields + '"' + field.column.upper() + '", '

            select_fields = select_fields[:-2]
            insert_fields = '(' + fields[:-2] + ')'

        print('select from', source)

        # Read all table data from postgress
        sql = f'select { select_fields } from { source } order by id'

        with connections[source_database].cursor() as cursor:
            #pg_cursor = connections['default'].cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            #pg_cursor.close()

        print('insert into', target)

        # Write to Oracle in bulk
        values_string = '%s, ' * field_count + '%s'
        stmt = f'INSERT INTO { target } { insert_fields } VALUES ({ values_string })'
        print(stmt)
        print(data[0])

        with connections[target_database].cursor() as cursor:
            if bulk:
                cursor.executemany(stmt, data)
            else:    
                for rec in data:
                    try:
                        cursor.execute(stmt, rec)
                    except:
                        print('error', rec)


        