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
        


    def get_ticket():
        return 'x'

    def submit_incident(self, route, action):


        headers = {
            'X-IBM-Client-Id': client_id,
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
            }

        text = self.data['reviewSummary']
        note = render_to_string('order/pinnacle_note.html', {'text': text, 'description': self.description})
 
        payload = route['constants']
        payload['Title'] = self.description
        payload['RequestorEmail'] = self.created_by.email
        payload['Description'] = f'{note}\n'

        # Add Attributes using target mapping
        field_map = action.override.get('map', '')

        display_values = {}
        for tab in self.data['reviewSummary']:
            for field in tab['fields']:
                if 'name' in field:
                    if 'list' in field:
                        nl = '\n'
                        display_values[field['name']] = nl.join(field['list'])
                    else:
                        display_values[field['name']] = field['value']

        attributes = []
        step_list = Step.objects.filter(action=action)
        element_list = Element.objects.filter(step__in=step_list, target__isnull=False)
        for element in element_list:
            value = display_values.get(element.name)
            if value:
                if element.name in field_map:
                    attributes.append({'ID': field_map[element.name], 'Value': value})
                else:
                    attributes.append({'ID': element.target, 'Value': value})

        if self.data['action_id'] == '67':
            db = self.data.get('database')
            if db:
                attributes.append({'ID': 5413, 'Value': db})

                if db == 'MSSQL':
                    attributes.append({'ID': 1994, 'Value': 215}) # Windows
                else:
                    attributes.append({'ID': 1994, 'Value': 216}) # Linux
            else:
                managed = self.data.get('managed')
                if managed:
                    os_name = Choice.objects.get(id=self.data.get('misevos')).code
                    attributes.append({'ID': 1952, 'Value': 203}) # Managed
                    if os_name.startswith('Windows'):
                        attributes.append({'ID': 1994, 'Value': 215}) # Windows
                    else:
                        attributes.append({'ID': 1994, 'Value': 216}) # Linux
                else:
                    attributes.append({'ID': 1952, 'Value': 207}) # Non-Managed
                    attributes.append({'ID': 1994, 'Value': 214}) # IAAS

            for field in text[1]['fields']:
                if field['label'] == 'Disk Space':
                    nl = '\n'
                    disks = nl.join(field['list'])
                    attributes.append({'ID': 1965, 'Value': disks})
            
        # Add Action Constants to Payload
        cons = Constant.objects.filter(action=action)

        for con in cons:  # Add Action Constants
            attributes.append({'ID': con.field, 'Value': con.value})

        payload['Attributes'] = attributes

        data_string = json.dumps(payload)
        response = requests.post( base_url + '/um/it/31/tickets', data=data_string, headers=headers )
 
        self.external_reference_id = json.loads(response.text)['ID']
        self.save()   # Save incident number to item


class ShortCodesAPI(UmAPI):
    SCOPE = 'shortcodes'
    PREFIX = 'bf'

    def __init__(self):
        self._get_token(self.SCOPE, self.PREFIX)

    def get_shortcode(self, shortcode):        
        url = f'{self.BASE_URL}/um/bf/ShortCodes/ShortCodes/{shortcode}'
        return requests.get(url, headers=self.headers)

