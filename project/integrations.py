import json, requests
from django.conf import settings
from ldap3 import Server, Connection, ALL

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
        #data = json.dumps(payload)
        #url = f'{self.BASE_URL}/31/tickets/'
        return requests.post( f'{self.BASE_URL}/31/tickets/'
                            , headers=self.headers
                            , json=payload )

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

    if instance.managed:
        os = instance.os.label
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
        "ResponsibleGroupID": 166,
        "Title": "Delete MiServer",
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
        ]
    }

    r = TDx().create_ticket(payload)
    if r.ok:
        print(r.status_code)
    else:
        print(r.status_code, r.text)

def create_ticket_database_modify(instance, user, description):

    payload = {
        "FormID": 19,
        "TypeID": 6,
        "SourceID": 4,
        "StatusID": 77,
        "ServiceID": 7,
        "ResponsibleGroupID": 17,
        "Title": "Modify MiDatabase Instance",
        "RequestorEmail": user.email,
        "Description": description,
        "Attributes": [
            {
                "ID": "1857", # Size
                "Value": str(instance.size)
            },
            {
                "ID": "1875",  # Shortcode
                "Value": "191248"
            },
            {
                "ID": "1859",  # Owner
                "Value": "ITS Planview Support"
            },
            {
                "ID": "1975",  # Support Email
                "Value": "its.pmo.ops@umich.edu"
            },
            {
                "ID": "1974",  # On Call
                "Value": "Contact me/my group only during business hours"
            },
            {
                "ID": "1842",
                "Value": "88"  # Modify
            }
        ]
    }

    client_id = settings.UM_API['CLIENT_ID']
    auth_token = settings.UM_API['AUTH_TOKEN']
    base_url = settings.UM_API['BASE_URL']

    headers = { 
        'Authorization': f'Basic {auth_token}',
        'accept': 'application/json'
        }

    url = f'{base_url}/um/it/oauth2/token?grant_type=client_credentials&scope=tdxticket'
    response = requests.post(url, headers=headers)
    response_token = json.loads(response.text)
    access_token = response_token.get('access_token')

    headers = {
        'X-IBM-Client-Id': client_id,
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json' 
        }

    data_string = json.dumps(payload)
    response = requests.post( base_url + '/um/it/31/tickets', data=data_string, headers=headers )
    print(response.status_code)