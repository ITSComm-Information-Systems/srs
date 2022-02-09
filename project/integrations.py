import json, requests
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


class UmAPI:
    CLIENT_ID = settings.UM_API['CLIENT_ID']
    AUTH_TOKEN = settings.UM_API['AUTH_TOKEN']
    BASE_URL = settings.UM_API['BASE_URL']

    def _get_token(self, scope, prefix):

        headers = { 
            'Authorization': f'Basic {self.AUTH_TOKEN}',
            'accept': 'application/json'
            }

        url = f'{self.BASE_URL}/um/{prefix}/oauth2/token?grant_type=client_credentials&scope={scope}'
        response = requests.post(url, headers=headers)
        response_token = json.loads(response.text)
        access_token = response_token.get('access_token')

        self.headers = {
            'X-IBM-Client-Id': self.CLIENT_ID,
            'Authorization': 'Bearer ' + access_token,
            #'Content-Type': 'application/json',
            'Accept': 'application/json' 
        }

        return access_token
        

class ShortCodesAPI(UmAPI):
    SCOPE = 'shortcodes'
    PREFIX = 'bf'

    def __init__(self):
        self._get_token(self.SCOPE, self.PREFIX)

    def get_shortcode(self, shortcode):        
        url = f'{self.BASE_URL}/um/bf/ShortCodes/ShortCodes/{shortcode}'
        return requests.get(url, headers=self.headers)


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

class PayloadCore():
    BASE = {
        "SourceID": 4,             # Web
        "StatusID": 77,            # Open
        "PriorityID": 20,          # Medium
    }

    DATABASE = {
        "FormID": 19,              # ITS-MiDatabase Account Requests - Form
        "TypeID": 6,               # Infrastructure / Compute Services
        "ServiceID": 7,            # ITS-MiDatabase Account Requests
        "ResponsibleGroupID": 17,  # ITS-MiDatabase
    }

    AWS = BASE | {
        "FormID": 152,            # ITS-Amazon Web Services at U-M Account Requests - Form
        "TypeID": 5,              # Cloud Services
        "ServiceID": 81,          # ITS-Amazon Web Services at U-M Account Requests
        "ResponsibleGroupID": 6,  # ITS-CloudComputeServices
    }

    AZURE = BASE | {
        "FormID": 16,              # ITS-Microsoft Azure at U-M Account Requests - Form
        "TypeID": 6,               # Cloud Services
        "ServiceID": 6,            # ITS-Microsoft Azure at U-M Account Requests
        "ResponsibleGroupID": 6,   # ITS-CloudComputeServices
    }

    GCP = BASE | {
        "FormID": 22,              # ITS-Google Cloud Platform at U-M Account Requests - Form
        "TypeID": 5,               # Cloud Services
        "ServiceID": 12,           # ITS-Google Cloud Platform at U-M Account Requests
        "ResponsibleGroupID": 6,   # ITS-CloudComputeServices
    }
    def get_payload(service):
        print(service)

    def get_payload_aws(self, action):
        New = 95
        Modify = 96
        Delete = 4699

        AWS = self.BASE | {
            "FormID": 152,            # ITS-Amazon Web Services at U-M Account Requests - Form
            "TypeID": 5,              # Cloud Services
            "ServiceID": 81,          # ITS-Amazon Web Services at U-M Account Requests
            "ResponsibleGroupID": 6,  # ITS-CloudComputeServices
        }

        self.add_attribute(1879, action)


    def add_attribute(self, id, attr):
        return 0

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

    def __init__(self, action, requester_email):
        
        self.data = {
            "FormID": self.form_id,
            "TypeID": self.type_id,
            "SourceID": self.source_id,
            "StatusID": self.status_id,
            "ServiceID": self.service_id,
            "ResponsibleGroupID": self.responsible_group_id,
            "Title": self.title,
            "RequestorEmail": requester_email,
            "Description": self.description,
            "Attributes": [] }




        #self.payload = self.BASE | self.payload
        self.add_attribute(self.request_type.id, getattr(self.request_type, action))


class ChoiceAttribute():
    
    def __init__(self, id, **kwargs):
        self.id = id
        for arg in kwargs:
            #print(arg)
            setattr(self, arg, kwargs[arg])


class AwsPayload(Payload):
    form_id = 152                # ITS-Amazon Web Services at U-M Account Requests - Form
    type_id = 5                  # Cloud Services
    service_id = 81              # ITS-Amazon Web Services at U-M Account Requests
    responsible_group_id = 6     # ITS-CloudComputeServices
    request_type = ChoiceAttribute(1879, New=95, Modify=96, Delete=4699)    
    title = 'Amazon Web Services at U-M'


class GcpPayload(Payload):
    form_id = 22                 # ITS-Amazon Web Services at U-M Account Requests - Form
    type_id = 5                  # Cloud Services
    service_id = 12,             # ITS-Amazon Web Services at U-M Account Requests
    responsible_group_id = 6     # ITS-CloudComputeServices
    request_type = ChoiceAttribute(1916, New=160, Modify=161, Delete=5465)
    project_id = 1997
    change_mc_group = ChoiceAttribute(1998, Yes=217, No=218)
    change_shortcode = ChoiceAttribute(2000, Yes=219, No=220)


def create_ticket(instance, action, post_data, user, **kwargs):
    service = type(instance).__name__
    service = service.upper()

    payload = globals()[service.capitalize() + 'Payload'](action, user.email)

    print(payload.data)

    #x = TDx().create_ticket(payload)
    #print(x.status_code, x.text)

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

