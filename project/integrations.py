import json, requests
from ssl import ALERT_DESCRIPTION_UNKNOWN_PSK_IDENTITY
from django.conf import settings
from ldap3 import Server, Connection, ALL, MODIFY_ADD


class MCommunity:

    def __init__(self):
        server = Server(settings.MCOMMUNITY['SERVER'], use_ssl=True, get_info=ALL)
        self.conn = Connection(server,
                        user=settings.MCOMMUNITY['USERNAME'],
                        password=settings.MCOMMUNITY['PASSWORD'],
                        auto_bind=True)

    def get_groups(self, uniqname):
        self.conn.search('ou=Groups,dc=umich,dc=edu', '(&(umichDirectMember=uid=' + uniqname + ',ou=People,dc=umich,dc=edu)(joinable=False))')

        group_list = []

        for entry in self.conn.entries:
            name = entry.entry_dn[3:-41]
            group_list.append(name)

        sorted_list = sorted(group_list, key=str.casefold)
        return sorted_list

    def get_group(self, name):
        self.conn.search('ou=Groups,dc=umich,dc=edu', '(cn=' + name + ')', attributes=["member"])

        if self.conn.entries:
            self.response = self.conn.entries
            self.dn = self.conn.entries[0].entry_dn[3:self.conn.entries[0].entry_dn.find(',')]

            self.members = set()

            for member in self.conn.entries[0]['member']:
                uid = member[4:member.find(',')]
                self.members.add(uid)  # Eliminate duplicates by adding to set

        else:
            print(f'none found for {name}')
            self = None

    def get_group_email(self, name):
        self.conn.search('ou=Groups,dc=umich,dc=edu', '(cn=' + name + ')', attributes=["umichGroupEmail"])

        try:
            umichGroupEmail = self.conn.entries[0].entry_attributes_as_dict['umichGroupEmail'][0]
            return umichGroupEmail + '@umich.edu'
        except:
            print(f'error getting email for {name}')

    def get_group_email_and_name(self, name):

        try:
            group = self.get_group_email(name)
            group = f'{name} | {group}'
            return group
        except:
            print('error getting MC group')
            return name

    def add_entitlement(self, name):
        new_member = f'cn={name},ou=User Groups,ou=Groups,dc=umich,dc=edu'
        parent_group = 'cn=SRS Service Entitlement Control,ou=User Groups,ou=Groups,dc=umich,dc=edu'

        x = self.conn.modify(parent_group, {'groupMember': [(MODIFY_ADD, [new_member])]})
        print('add', x, self.conn.response)

    def get_user(self, uniqname):
        self.conn.search('ou=People,dc=umich,dc=edu', '(uid=' + uniqname + ')', attributes=["uid","mail","user","givenName","umichDisplaySn","umichInstRoles","umichHR"])

        if self.conn.entries:
            return self.conn.entries[0]
        else:
            return None


class UmAPI:
    AUTH_TOKEN = settings.UM_API['AUTH_TOKEN']
    BASE_URL = settings.UM_API['BASE_URL']

    def _get_token(self, scope):
        
        headers = { 
            'Authorization': f'Basic {self.AUTH_TOKEN}',
            'accept': 'application/json'
            }

        url = f'{self.BASE_URL}/um/oauth2/token?grant_type=client_credentials&scope={scope}'
        response = requests.post(url, headers=headers)
        response_token = json.loads(response.text)
        access_token = response_token.get('access_token')

        self.headers = {
            'Authorization': 'Bearer ' + access_token,
            'Accept': 'application/json' 
        }

        return access_token
        

class ShortCodesAPI(UmAPI):
    SCOPE = 'shortcodes'
    PREFIX = 'bf'

    def __init__(self):
        self._get_token(self.SCOPE)

    def get_shortcode(self, shortcode):        
        url = f'{self.BASE_URL}/um/bf/ShortCodes/ShortCodes/{shortcode}'
        return requests.get(url, headers=self.headers)

class Openshift():

    BASE_URL = settings.OPENSHIFT['BASE_URL']
    USER = settings.OPENSHIFT['USER']
    TOKEN = settings.OPENSHIFT['TOKEN']
    PROJECT_URL = BASE_URL + '/apis/project.openshift.io/v1/projects'

    def get_project(self, name):
        headers = {'Authorization': f'Bearer {self.TOKEN}'}        
        #r = requests.get(f'{self.PROJECT_URL}/{name}', headers=headers)
        r = requests.get(f'{self.PROJECT_URL}/', headers=headers)
        print(r.status_code, r.text)        

    def create_project(self, name):
        payload = {"metadata":{"name": name}}
        headers = {'Authorization': f'Bearer {self.TOKEN}'}        
        r = requests.post(f'{self.PROJECT_URL}', headers=headers, json=payload)
        print(r.status_code, r.text)      


class TDx():
    BASE_URL = settings.TDX['URL']
    USERNAME = settings.TDX['USERNAME']
    PASSWORD = settings.TDX['PASSWORD']

    def get_ticket(self, id):
        url = f'{self.BASE_URL}/tickets/{id}'
        return requests.get( url, headers=self.headers )

    def create_ticket(self, payload):
        payload['SourceID'] = 8         # System

        resp = requests.post( f'{self.BASE_URL}/31/tickets/'
                            , headers=self.headers
                            , json=payload )

        if not resp.ok:
            print(resp.status_code, resp.text)

        return resp

    def __init__(self):
        self._get_token()

    def _get_token(self):
        url = self.BASE_URL + '/auth'

        headers = {'Content-Type': 'application/json; charset=utf-8'}

        data = {
            'username': self.USERNAME,
            'password': self.PASSWORD
        }

        data_string = json.dumps(data)
        response = requests.post(url, data=data_string, headers=headers )

        if response.ok:
            self.headers = {
                'Authorization': 'Bearer ' + response.text,
                'Content-Type': 'application/json',
                'Accept': 'application/json' 
                }
        else:
            print(response, response.status_code, response.text)


def create_ticket_server_delete(instance, user, description):
    
    os = getattr(instance.os, 'label', '')

    if instance.managed:
        if os.startswith('Windows'):
            miserver_Managed = '215' # Windows
        else:
            miserver_Managed = '216' # Linux
    else:
        miserver_Managed = '214' # IAAS

    payload = {
        "FormID": 24,
        "TypeID": 7,
        "SourceID": 0,
        "StatusID": 77,
        "ServiceID": 10,
        "ResponsibleGroupID": 18,
        "Title": description,
        "RequestorEmail": user.email,
        "Description": description,
        "Attributes": [
            {
                "ID": "1951", 
                "Value": "202"  # Delete
            },
            {
                "ID": "1959",  # Server Name
                "Value": instance.name
            },
            {
                "ID": "1994",  # Managed
                "Value": miserver_Managed
            },
            {
                "ID": "1957",  # miserver_Operation System
                "Value": os
            },
        ]
    }
    
    if instance.database_type:
        payload['Attributes'].append({"ID": "5319", "Value": instance.database_type.__str__()})

    TDx().create_ticket(payload)


class Payload():
    title = 'SRS Request'
    description = title
    Web = 4
    Open = 77
    Medium = 20

    source_id = Web
    status_id = Open
    priority_id = Medium

    def add_attribute(self, id, value):
        self.data['Attributes'].append(
            {
                "ID": id, 
                "Value": value
            }
        )

    def __init__(self, action, instance, request, **kwargs):
        
        self.data = {
            "FormID": self.form_id,
            "TypeID": self.type_id,

            #"UrgencyName": "High",

            "SourceID": self.source_id,
            "StatusID": self.status_id,
            "ServiceID": self.service_id,
            "ResponsibleGroupID": self.responsible_group_id,
            "Title": self.title,
            "RequestorEmail": request.user.email,
            "Description": self.description,
            "Attributes": [] } | kwargs

        if request.POST.get('sensitive_data_yn') == 'Yes':
            value = ''
            for val in instance.regulated_data.values() | instance.non_regulated_data.values():
                if hasattr(self.sensitive_data, val['code']):
                    tdx_id = getattr(self.sensitive_data, val['code'])
                else:
                    tdx_id = getattr(self.sensitive_data, 'OTHERNONREG')

                if value == '':
                    value = str(tdx_id)
                else:
                    value = value + ',' + str(tdx_id)

            self.add_attribute(self.sensitive_data.id, value)

        for key, value in request.POST.items():
            if key in dir(self):
                attr = getattr(self, key)
                val = attr.get_value(value) #getattr(attr, value)
                if val == '':
                    if hasattr(instance, key):    # not found so check to see if choice code exists and use that
                        f = getattr(instance, key)
                        if hasattr(f, 'code'):
                            code = getattr(f, 'code')
                            val = getattr(attr, code)
                
                self.add_attribute(attr.id, val)
            else:
                print('not found', key)

        if action == 'Delete':
            self.add_attribute(self.delete_account.id, instance.account_id)
            self.add_attribute(self.delete_owner.id, instance.owner.name)
            self.add_attribute(self.delete_acknowledgement.id, self.delete_acknowledgement.Yes)
            #self.add_attribute(self.delete_vpn.id, instance.vpn)

        #self.payload = self.BASE | self.payload
        self.add_attribute(self.request_type.id, getattr(self.request_type, action))


class ChoiceAttribute():
    
    def __init__(self, id, **kwargs):
        self.id = id
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])
    
    def get_value(self, value):
        if hasattr(self, value):
            val = getattr(self, value)
            return val
        else:
            print('not found', value)
            return ''

class TextAttribute():
    
    def __init__(self, id, **kwargs):
        self.id = id

    def get_value(self, value):
        return value


class AwsPayload(Payload):
    form_id = 152                # ITS-Amazon Web Services at U-M Account Requests - Form
    type_id = 5                  # Cloud Services
    service_id = 81              # ITS-Amazon Web Services at U-M Account Requests
    responsible_group_id = 6     # ITS-CloudComputeServices
    request_type = ChoiceAttribute(1879, New=95, Modify=96, Delete=4699)    # Azure Request Options
    contact_email = TextAttribute(1780)
    contact_phone = TextAttribute(1781)
    migrate_existing = ChoiceAttribute(1881, No=100, Yes=99)
    aws_email = TextAttribute(1882)
    aws_account_number = TextAttribute(1883)
    admin_group = TextAttribute(1884)
    billing_contact = TextAttribute(1885)
    shortcode = TextAttribute(1886)
    sensitive_data_yn = ChoiceAttribute(1887, No=102, Yes=101)
    sensitive_data = ChoiceAttribute(1888,HIPAA=103,FERPA=104,GLBA=105,HSR=106,SSN=107,ATT=108,PPI=109,ITSEC=110,PCI=111,ECR=112,FISMA=113,OTHERNONREG=114)
    security_contact = TextAttribute(1889)
    region_yn = ChoiceAttribute(1890, No=116, Yes=115)
    region = ChoiceAttribute(1891,USEastNVA=117,USEastOH=118,USWestNCA=119,USWestOR=120,
                APTokyo=121,APSeoul=122,APMumbai=123,APSingapore=124,APSydney=125,Canada=126,
                ChinaBejing=127,ChinaNingxia=128,EUFrankfurt=129,EUIreland=130,EULondon=131,EUParis=132,SASaoPaulo=133)

    egress_waiver = ChoiceAttribute(1893, No=135, Yes=134)
    redhat = ChoiceAttribute(1894, No=137, Yes=136)
    vpn = ChoiceAttribute(1895, No=139, Yes=138)
    request_consultation = ChoiceAttribute(1896, No=141, Yes=140)
    acknowledge_sle = ChoiceAttribute(1898, Yes=142)
    acknowledge_srd = ChoiceAttribute(3589, Yes=3026)


    #aws_account_number = TextAttribute(1901)
    #change_mc_group = ChoiceAttribute(1902, No=145, Yes=144)    # aws_modify_Change MCommunity Group?
    #change_billing_contact = ChoiceAttribute(1906, No=149, Yes=148 )
    delete_account = TextAttribute(4327)
    delete_owner = TextAttribute(4315)
    delete_acknowledgement = ChoiceAttribute(4316, Yes=4698)
    title = 'Amazon Web Services at U-M'


class GcpPayload(Payload):
    form_id = 22                 # ITS-Amazon Web Services at U-M Account Requests - Form
    type_id = 5                  # Cloud Services
    service_id = 12              # ITS-Amazon Web Services at U-M Account Requests
    responsible_group_id = 6     # ITS-CloudComputeServices
    request_type = ChoiceAttribute(1916, New=160, Modify=161, Delete=5465)
    contact_email = TextAttribute(1780)
    contact_phone = TextAttribute(1781)
    existing_yn = ChoiceAttribute(1914, No=159, Yes=158)
    existing_id = TextAttribute(1915)
    existing_project = TextAttribute(1919)
    billing_yn = ChoiceAttribute(1921, No=163, Yes=162)
    billing_id = TextAttribute(1922)
    billing_attach_project = ChoiceAttribute(4664, No=5441, Yes=5440)
    billing_attach_id = TextAttribute(4665)
    admin_group = TextAttribute(1923)
    shortcode = TextAttribute(1924)
    billing_contact = TextAttribute(1926)
    security_contact = TextAttribute(1927)
    egress_waiver = ChoiceAttribute(1929, No=165, Yes=164)
    sensitive_data_yn = ChoiceAttribute(1931, No=167, Yes=166)
    sensitive_data = ChoiceAttribute(1933,HIPAA=168,FERPA=169,GLBA=170,HSR=171,SSN=172,ATT=173,PPI=174,ITSEC=175,PCI=176,ECR=177,FISMA=178,OTHERNONREG=179)
    network = ChoiceAttribute(1934, No=181, Yes=180)
    redhat = ChoiceAttribute(1935, No=183, Yes=182)
    vpn = ChoiceAttribute(1936, No=185, Yes=184)
    request_consultation = ChoiceAttribute(1937, No=187, Yes=186)
    acknowledge_sle = ChoiceAttribute(1940, Yes=192)
    acknowledge_srd = ChoiceAttribute(1942, Yes=195)
    additional_details = TextAttribute(3590)

    delete_vpn = TextAttribute(4742)
    delete_account = TextAttribute(4692)
    delete_owner = TextAttribute(4693)
    delete_acknowledgement = ChoiceAttribute(4694, Yes=5466)

    nih_yn = ChoiceAttribute(8930, Yes=22957, No=22958)
    nih_id = TextAttribute(8932)
    nih_officer_name = TextAttribute(8933)
    nih_officer_email = TextAttribute(8934)

    title = 'Google Cloud Platform at U-M'

class AzurePayload(Payload):
    form_id = 16
    type_id = 5   # 5 for delete?
    service_id = 6
    responsible_group_id = 6
    request_type = ChoiceAttribute(1786, New=19, Modify=20, Delete=4766)    
    admin_group = TextAttribute(1802)
    shortcode = TextAttribute(1798)
    billing_contact = TextAttribute(1804)
    security_contact = TextAttribute(1800)
    security_contact_phone = TextAttribute(1799)
    sensitive_data_yn = ChoiceAttribute(1788, No=24, Yes=23)
    sensitive_data = ChoiceAttribute(1814,ATT=53,PCI=56,ECR=57,FISMA=58,HSR=51,ITSEC=55,OTHERNONREG=59,PPI=54,HIPAA=48,SSN=52,FERPA=49,GLBA=50)
    vpn = ChoiceAttribute(1787, No=22, Yes=21)
    vpn_tier = ChoiceAttribute(1813, Basic=44, VpnGw1=45, VpnGw2=46, VpnGw3=47)
    request_consultation = ChoiceAttribute(1801, No=40, Yes=41)
    additional_details = TextAttribute(1805)
    acknowledge_sle = ChoiceAttribute(1797, Yes=39)
    acknowledge_srd = ChoiceAttribute(2493, Yes=1100)
    # Delete
    #account_id = TextAttribute(1796)

    delete_account = TextAttribute(1796)
    delete_owner = TextAttribute(4690)
    delete_acknowledgement = ChoiceAttribute(4691, Yes=5464)

def create_ticket(action, instance, request, **kwargs):
    service = type(instance).__name__
    service = service.upper()

    payload = globals()[service.capitalize() + 'Payload'](action, instance, request, **kwargs)
    #print(payload.data)

    resp = TDx().create_ticket(payload.data)
    if not resp.ok:
        print('TDx response', resp.status_code, resp.text)

def create_ticket_database_modify(instance, user, description):

    payload = {
        "FormID": 19,              # ITS-MiDatabase Account Requests - Form
        "TypeID": 6,               # Compute Services
        "SourceID": 4,             #
        "StatusID": 77,            # Open
        "ServiceID": 7,            # ITS-MiDatabase Account Requests
        "ResponsibleGroupID": 17,  # ITS-MiDatabase
        "Title": "Modify MiDatabase Instance",
        "RequestorEmail": user.email,
        "Description": description,
        "Attributes": [
            {
                "ID": "1855", # Name
                "Value": instance.name
            },
            {
                "ID": "1857", # Size
                "Value": str(instance.size)
            },
            {
                "ID": "1858", # Type
                "Value": instance.type.label
            },
            {
                "ID": "1875",  # Shortcode
                "Value": instance.shortcode
            },
            {
                "ID": "1859",  # Owner
                "Value": instance.owner.name
            },
            {
                "ID": "1975",  # Support Email
                "Value": instance.support_email
            },
            {
                "ID": "1974",  # On Call
                "Value": instance.on_call
            },
            {
                "ID": "1842",
                "Value": "88"  # Modify
            }
        ]
    }

    TDx().create_ticket(payload)

