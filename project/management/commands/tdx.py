from http.client import REQUEST_URI_TOO_LONG
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from project.integrations import UmAPI, MCommunity, TDx, AwsPayload
from services.models import AWS
from django.contrib.auth.models import User
import requests, json


payload = {
    "FormID": 19,
    "TypeID": 6,
    "SourceID": 4,
    "StatusID": 77,
    "ServiceID": 7,
    "PriorityID": 20,
    "ResponsibleGroupID": 17,
    "Title": "md mdb Instance",
#    "RequestorUid": '2d3898e5-7a73-ea11-a81b-000d3a8e391e',
    "RequestorEmail": 'djamison@umich.edu',
    "Description": 'test',

        "Attributes": [
            {
                "ID": "1951", 
                "Value": "202"  # Delete
            },
            {
                "ID": "1959",  # Server Name
                "Value": 'venus'
            },
            {
                "ID": "1994",  # Managed
                "Value": 202
            },
        ]
}

class Command(BaseCommand):
    help = 'TDx read API Data'

    def add_arguments(self, parser):
        parser.add_argument('--ticket')
        parser.add_argument('--attr')
        parser.add_argument('--parent')
        parser.add_argument('--choices')


    def handle(self, *args, **options):

        x = AwsPayload('Delete')
        print(x.payload)

        return

        aws = AWS.objects.get(id=243)
        user = User.objects.get(username='djamison')
        post_data = {'csrfmiddlewaretoken': ['L37YATeBoCVF7vtMbV9B84Ocj0rlcL6Yc4aoN4Wi6Go0tjaR8wdOtsIkV36rd1VW'], 'requestor': ['djamison'], 'owner_group': ['grp'], 'contact_phone': ['734-867-5309'], 'short_code': ['940479'], 'migrate': ['No'], 'redhat': ['No'], 'vpn': ['No'], 'consult': ['No']}
        create_ticket(aws, 'ADD', post_data, user, title='Amazon Web Services at U-M')

        if options['ticket']:
            tdx = TDx()
            r = tdx.get_ticket(options['ticket'])
            print(r.text)

        if options['attr']:
            tdx = TDxAdmin()
            r = tdx.get_attribute_by_id(options['attr'])
            
        if options['choices']:
            tdx = TDxAdmin()
            r = tdx.get_choices(options['choices'])

        if options['parent']:
            tdx = TDxAdmin()
            print(options['parent'])
            r = tdx.get_child_attributes(options['parent'])


class TDxAdmin():

    BASE_URL = 'https://teamdynamix.umich.edu/SBTDWebApi/api'  # Sandbox only

    def get_ticket(self, id):
        url = f'{self.BASE_URL}/tickets/{id}'
        response = requests.get( url, headers=self.headers )
        print(response, response.status_code, response.text)   

    def get_attributes(self):
        url = f'{self.BASE_URL}/attributes/custom?componentId=9'
        response = requests.get( url, headers=self.headers )
        print(response, response.status_code)
        return json.loads(response.text)

    def get_attribute_by_id(self, id):
        attr_list = self.get_attributes()
        id = int(id)
        for attr in attr_list:
            if attr['ID'] == id:
                formatted = json.dumps(attr, indent=2)
                print(formatted)

    def get_child_attributes(self, parent_id):
        attr_list = self.get_attributes()
        #print('attrs', parent_id, type(parent_id))
        parent_id = int(parent_id)
        print(attr_list)
        for attr in attr_list:
            if attr['ParentAttributeID'] == parent_id:
                print(attr['ID'], attr['Name'])

    def get_choices(self, id):
        url = f'{self.BASE_URL}/attributes/{id}/choices'
        response = requests.get( url, headers=self.headers )
        print(response, response.status_code, response.text)     

    def __init__(self):
        print('get token')
        self._get_token()

    def _get_token(self):
        url = self.BASE_URL + '/auth/loginadmin'

        headers = {'Content-Type': 'application/json; charset=utf-8'}

        data = {
            'BEID': settings.TDX_ADMIN['BEID'],
            'WebServicesKey': settings.TDX_ADMIN['KEY']
        }

        data_string = json.dumps(data)
        response = requests.post(url, data=data_string, headers=headers )

        print(response, response.status_code, response.text)

        self.headers = {
            'Authorization': 'Bearer ' + response.text,
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
            }
