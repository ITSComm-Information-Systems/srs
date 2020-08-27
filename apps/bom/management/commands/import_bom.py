from django.core.management.base import BaseCommand, CommandError
from django.db import connections
import requests, json
from decimal import Decimal

from apps.bom.models import LegacyData, Estimate, Material, Labor, Project, Technician

class Command(BaseCommand):
    help = 'Import BOM Data from ServiceNow'

    def handle(self, *args, **options): 
        ServiceNow().load_all_tables()
        #sn = ServiceNow()
        #sn.load_all_records('u_bom_labor_estimate')
        #sn.test_sql()


class ServiceNow:
    URL = 'https://umichprod.service-now.com/api/now/table/'
    AUTH = ('soap.bom', 'magpie')
    TABLES = [
        'u_bill_of_material',
        'u_bill_of_material_detail',
        'u_bom_labor_estimate'
        ]
    PAGE_SIZE = 1000
    user_list = {}

    GROUPS = {'07282fbd6f1c6180461a792f8e3ee4f7':'AS1', # Dict of SN ID vs Pinnacle ID
            'c976a3bd6f1c6180461a792f8e3ee401':'OTH',
            'e508e77d6f1c6180461a792f8e3ee496':'SW1',
            '3ef72fbd6f1c6180461a792f8e3ee4be':'DR1',
            '79d8afbd6f1c6180461a792f8e3ee49d':'EN1',
            'cf0927fd6f1c6180461a792f8e3ee484':'WNC',
            '98f8e3fd6f1c6180461a792f8e3ee421':'FS1',
            'b8e8e3fd6f1c6180461a792f8e3ee428':'OST',
            '880927fd6f1c6180461a792f8e3ee408':'NA',
            '691927fd6f1c6180461a792f8e3ee48b':'PCT',
            'ea18af3d6f1c6180461a792f8e3ee445':'PM2',
            'b4c863bd6f1c6180461a792f8e3ee490':'WH1',
            'e21756f06f10d20011ba7b11be3ee485':'VT'}

    def get_page(self, table, limit, offset):
        resp = requests.get(f"{self.URL}{table}?sysparm_limit={limit}&sysparm_offset={offset}" #&sysparm_query=sys_created_on>javascript:gs.dateGenerate('2019-01-01','23:59:59')"
            ,auth=self.AUTH )
        data = json.loads(resp.text)

        return data.get('result', None)

    def _cast_int(self, record, field):
        num = None
        value = record.get(field)
        if value:
            try:
                num = int(value)
            except:
                pk = record['sys_id']
                print(f'Error: {field}:{value} in {pk}')
            
        return num

    def _cast_dec(self, record, field):
        value = record.get(field)
        if value:
            try:
                num = Decimal(value)
                if num < 999999:
                    return num
                else:
                    error = 'Number too large'
            except:
                error = 'Number conversion error'

            pk = record['sys_id']
            print(f'{error}: {field}:{value} in {pk}')

        return None                


    def load_all_records(self, table):
        offset = 0
        count = 0

        while True:
            data = self.get_page(table, self.PAGE_SIZE, offset)

            instances = []

            for record in data:
                count +=1

                lg = LegacyData()
                lg.sys_id = record['sys_id']
                lg.record_name = table
                lg.create_date = record['sys_created_on']
                lg.created_by = record['sys_created_by']
                lg.update_date = record['sys_updated_on']
                lg.updated_by = record['sys_updated_by']

                if lg.created_by == 'mafaith' or lg.created_by == 'UM Admin':
                    lg.created_by = 'ServiceNow'

                if lg.updated_by == 'mafaith' or lg.updated_by == 'UM Admin':
                    lg.updated_by = 'ServiceNow'

                parent = record.get('u_bill_of_material')
                if parent:
                    lg.parent_sys_id = parent.get('value')

                if table == 'u_bill_of_material':
                    lg.woid = self._cast_int(record, 'u_woid')
                    lg.multi = self._cast_int(record, 'u_multi')
                    lg.contingency_percentage = self._cast_dec(record, 'u_contingency_percentage')
                    lg.contingency_amount = self._cast_dec(record, 'u_contingency_dollars')
                    location = record.get('u_building_name')
                    if location:
                        lg.location_name = location.get('value')
                    lg.status = record.get('u_bom_status')

                    pe = record.get('u_project_engineer')
                    if pe:
                        lg.assigned_engineer = self.get_username(  pe.get('value') )
                        #lg.location_name = location.get('value')

                    self.add_umnet_record(record)

                elif table == 'u_bill_of_material_detail':
                    lg.quantity = self._cast_int(record, 'u_quantity') #record['u_quantity']
                    lg.price = record['u_order_unit_price']

                    item = record.get('u_item_')
                    if item:
                        lg.commodity_code = item.get('value')

                    lg.addl_1 = record['u_manufacturer']
                    lg.addl_2 = record['u_manufacturer_part_number']
                    lg.commodity_descr = record['u_item_description']
                    lg.status = record['u_material_status']
                    
                    lg.location_name = record['u_location']
                    lg.location_descr = record['u_location_notes']
                    lg.commodity_descr = record['u_item_description']


                    vendor = record.get('u_vendor')
                    if vendor:
                        sys_id = vendor['value']
                        if sys_id: 
                            lg.vendor = self.vendor_list[sys_id]
                            #print(vendor)
                    
                    reel_number = record.get('u_reel_number')
                    if reel_number:
                        sys_id = reel_number['value']
                        if sys_id:
                            lg.reel_number = self.reel_list[sys_id]


                    staged = record.get('u_staged')
                    if staged == 'Yes':
                        lg.staged = True
                    order_date = record.get('u_order_date')
                    if order_date:
                        lg.order_date = order_date

                    estimated_receive_date = record.get('u_estimated_receive_date')
                    if estimated_receive_date:
                        lg.estimated_receive_date = estimated_receive_date

                    lg.release_number = record['u_release_']



                elif table == 'u_bom_labor_estimate':
                    lg.hours = self._cast_dec(record, 'u_labor_hours_estimate')
                    lg.price = self._cast_dec(record, 'u_labor_rate')
                    lg.commodity_descr = record['u_description']
                    lg.commodity_code = record['u_labor_type']

                    group = record.get('u_group')
                    if group:
                        lg.addl_1 = group['value']
                        lg.addl_2 = self.GROUPS[lg.addl_1]

                elif table == 'u_pin_commodity':
                    lg.commodity_code = record['u_item_code']

                #lg.data = json.dumps(data)
                instances.append(lg)
                #print('append', count)

            LegacyData.objects.bulk_create(instances)

            offset = offset + self.PAGE_SIZE
            print(table ,count)

            if len(data) < self.PAGE_SIZE:
                break

    def add_umnet_record(self, record):

        tech = record.get('u_ios_technician')
        ad = record.get('u_ios_assigned_date')
        dd = record.get('u_ios_due_date')
        cd = record.get('u_ios_completed_date')
        status = record.get('u_ios_project_status')
        pct = record.get('u_ios_percent_completed')
        health = record.get('u_ios_project_health')
        notes = record.get('u_ios_notes')
        user_name = ''

        if tech:
            sys_id = tech.get('value')
            if len(sys_id) == 32:
                user_name = self.get_username(sys_id)

        if status+ad+dd+cd+pct+health != 'Green':
            proj = Project()

            proj.create_date = record['sys_created_on']
            proj.created_by = record['sys_created_by']
            proj.update_date = record['sys_updated_on']
            proj.updated_by = record['sys_updated_by']

            if proj.created_by == 'mafaith' or proj.created_by == 'UM Admin':
                proj.created_by = 'ServiceNow'

            if proj.updated_by == 'mafaith' or proj.updated_by == 'UM Admin':
                proj.updated_by = 'ServiceNow'

            for i in proj.STATUS_CHOICES:
                if i[1] == status:
                    status = i[0]


            for i in proj.PROJECT_HEALTH_CHOICES:
                if i[1] == health:
                    health = i[0]

            proj.netops_engineer_id = user_name
            proj.woid = 0
            proj.status = status
            if pct:
                proj.percent_completed = int(pct)
            proj.health = health
            if dd:
                proj.due_date = dd
            if cd:
                proj.completed_date = cd
            if ad:
                proj.active_date = ad
            proj.legacy_parent_id = record['sys_id']
            try:
                proj.save()
            except:
                print(f'error~{user_name}~{status}~{ad}~{dd}~{cd}~{pct}~{health}')


    def get_username(self, sys_id):
        user = self.user_list.get(sys_id)

        if user:
            return user
        else:
            #print('lookup', sys_id)
            resp = requests.get(f"{self.URL}sys_user?sys_id={sys_id}"
                ,auth=self.AUTH )
            data = json.loads(resp.text)

            try:
                user_name = data['result'][0]['user_name']
                id = self.tech_table[user_name]
            except:
                id = 0
            
            self.user_list[sys_id] = id
            #print('lookup', user_name, sys_id)
            return id
            
    def get_vendor_list(self):
            self.vendor_list = {}
            resp = requests.get(f"{self.URL}u_pin_vendor" ,auth=self.AUTH )
            data = json.loads(resp.text)
            #print(data)
            for record in data['result']:
                self.vendor_list[record['sys_id']] = record['u_id']

    def get_reel_list(self):
            self.reel_list = {}
            resp = requests.get(f"{self.URL}u_remedy_cable_reel" ,auth=self.AUTH )
            data = json.loads(resp.text)
            #print(data)
            for record in data['result']:
                self.reel_list[record['sys_id']] = record['u_reel_number']

    def get_location_data(self):

        sql = "select distinct location_name from um_bom_legacy_data where record_name = 'u_bill_of_material' and length(location_name)=32"

        with connections['pinnacle'].cursor() as cursor:
            cursor.execute(sql)
            locations = cursor.fetchall()

        for location in locations:
            #print(location[0])
            sys_id = location[0]

            if sys_id:
        
                resp = requests.get(f"{self.URL}cmn_location?sys_id={location[0]}" 
                    ,auth=self.AUTH )
                data = json.loads(resp.text)

                building_number = data['result'][0]['u_building_number']

                if building_number:
                    lg = LegacyData()
                    lg.record_name = 'location'
                    lg.sys_id = sys_id
                    lg.u_building_name = building_number
                    lg.save()

    def load_techs(self):
        self.tech_table = {}

        for tech in Technician.objects.all():
            self.tech_table[tech.user_name] = tech.id

        print('tech list loaded')
        #print(self.tech_table)



    def load_all_tables(self):
        self.load_techs()        
        self.load_all_records('u_bill_of_material')
        self.get_location_data()
        self.get_vendor_list()
        self.get_reel_list()
        self.load_all_records('u_bill_of_material_detail') 
        self.load_all_records('u_bom_labor_estimate')
        self.load_all_records('u_pin_commodity')

        with connections['pinnacle'].cursor() as cursor:
            # Truncate tables
            cursor.execute('truncate table um_bom_material_location')
            cursor.execute('truncate table um_bom_material')
            cursor.execute('delete from um_bom_estimate')
            print('target tables truncated')

            # Load Estimate Table
            cursor.execute("insert into um_bom_estimate (assigned_engineer_id, create_date, created_by, update_date, updated_by, woid, status, label, contingency_amount, contingency_percentage, legacy_id)  "
                            "select assigned_engineer, create_date, created_by, update_date, updated_by, woid, decode(status,'Estimate',1,0,1,1,2,2,3,status), 'Multi-' || multi, contingency_amount, contingency_percentage, sys_id "
                            "from um_bom_legacy_data where record_name = 'u_bill_of_material' "
                            "order by to_char(create_date,'YYYYMMDD'), woid, multi ")
            print(cursor.rowcount, 'estimate records loaded')

            cursor.execute("update um_bom_legacy_data a "
                            "set new_record_id = (select id from um_bom_estimate where legacy_id = a.parent_sys_id) ")
            print(cursor.rowcount, 'updated new_record_id')

            # Point Project data to estimates
            cursor.execute("update um_bom_project a "
                            "set a.woid = (select max(b.woid) "
                            "from um_bom_estimate b "
                            "where a.legacy_parent_id = b.legacy_id) ")
            print(cursor.rowcount, 'set project woid')

            cursor.execute("update um_bom_project a set woid = -1 "
                           "where exists (select 'x' from um_bom_project where woid = a.woid and id > a.id) ")
            print(cursor.rowcount, 'clear duplicates') #TODO
            

            # Load Material_Location Table
            cursor.execute("update um_bom_legacy_data set location_name = 'Main' where record_name = 'u_bill_of_material_detail' and location_name is null")
            print(cursor.rowcount, 'set default location')

            cursor.execute("insert into um_bom_material_location (estimate_id, name, description, create_date, created_by, update_date, updated_by) "
                            "select new_record_id, substr(location_name, 1,32), location_descr, min(create_date), stats_mode(created_by), max(update_date), stats_mode(updated_by) "
                            "from um_bom_legacy_data "
                            "where record_name = 'u_bill_of_material_detail' "
                            "and new_record_id is not null "
                            "group by new_record_id, substr(location_name, 1,32), location_descr") 
            print(cursor.rowcount, 'material_location records created')

            # Load Material Table
            cursor.execute("update um_bom_legacy_data a "
                            "set commodity_id = (select commodity_id "
                                                "from axis.commodity_api_v "
                                                "where commodity_code = a.commodity_code) "
                            "where record_name = 'u_pin_commodity' ")
            print(cursor.rowcount, 'update commodity_id for u_pin_commodity')

            cursor.execute("update um_bom_legacy_data a "
                            "set (commodity_id, commodity_code) = (select commodity_id, commodity_code "
                                                "from um_bom_legacy_data "
                                                "where sys_id = a.commodity_code "
                                                "  and record_name = 'u_pin_commodity') "
                            "where record_name = 'u_bill_of_material_detail' ")
            print(cursor.rowcount, 'update commodity_id for bom_detail')

            cursor.execute("update um_bom_legacy_data set commodity_code = '' where length(commodity_code) = 32")
            print(cursor.rowcount, 'clear commodity_code')

            cursor.execute("insert into um_bom_material (create_date, created_by, update_date, updated_by, item_id, item_code, item_description "
                        ", quantity, price, status, material_location_id, vendor, reel_number, staged, order_date,  ESTIMATED_RECEIVE_DATE ,RELEASE_NUMBER, manufacturer, manufacturer_part_number  ) "
                        "select a.create_date, a.created_by, a.update_date, a.updated_by, a.commodity_id, a.commodity_code, a.commodity_descr "
                        ", a.quantity, a.price, decode(a.status,'Estimate',1,'In Stock',2,'Ordered',3), b.id, vendor, reel_number, staged, order_date,  ESTIMATED_RECEIVE_DATE ,RELEASE_NUMBER, addl_1, addl_2 "
                        "from um_bom_legacy_data a, um_bom_material_location b "
                        "where a.new_record_id = b.estimate_id "
                        "  and a.location_name = b.name "
                        "  and a.record_name = 'u_bill_of_material_detail' "
                        "  and quantity is not null ")
            print(cursor.rowcount, 'material records created')

            # Load Labor Table
            cursor.execute("insert into um_bom_labor (create_date, created_by, update_date, updated_by, estimate_id, description, group_id, rate_type, hours, rate ) "
                            "select create_date, created_by, update_date, updated_by, new_record_id, commodity_descr, addl_2, decode(commodity_code,'0',1,'1','2'), hours, price "
                            "from um_bom_legacy_data where record_name = 'u_bom_labor_estimate' "
                            "and new_record_id is not null and hours is not null and addl_2 is not null ")
            print(cursor.rowcount, 'labor records created')

    def test_sql(self):

        with connections['pinnacle'].cursor() as cursor:
            cursor.execute('truncate table um_bom_material')


            cursor.execute("insert into um_bom_material (create_date, created_by, update_date, updated_by, item_id, item_code, item_description "
                        ", quantity, price, status, material_location_id, vendor, reel_number, staged, order_date,  ESTIMATED_RECEIVE_DATE ,RELEASE_NUMBER, manufacturer, manufacturer_part_number  ) "
                        "select a.create_date, a.created_by, a.update_date, a.updated_by, a.commodity_id, a.commodity_code, a.commodity_descr "
                        ", a.quantity, a.price, decode(a.status,'Estimate',1,'In Stock',2,'Ordered',3), b.id, vendor, reel_number, staged, order_date,  ESTIMATED_RECEIVE_DATE ,RELEASE_NUMBER, addl_1, addl_2 "
                        "from um_bom_legacy_data a, um_bom_material_location b "
                        "where a.new_record_id = b.estimate_id "
                        "  and a.location_name = b.name "
                        "  and a.record_name = 'u_bill_of_material_detail' "
                        "  and quantity is not null ")
            print(cursor.rowcount, 'material records created')