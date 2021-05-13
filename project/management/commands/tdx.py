from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from project.integrations import UmAPI, MCommunity, TDx


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
        tdx = TDx()
        #r = tdx.get_ticket(873987)
        #print(r.text)
        #return

        print(payload)
        r = tdx.create_ticket(payload)
        if r.ok:
            print(r.status_code)
        else:
            print(r.status_code, r.text)

        return

        if 'ticket' in options:
            r = tdx.get_ticket(options['ticket'])
            print(r.status_code, r.text)

        if 'choices' in options:
            r = tdx.get_choices(options['choices'])
            print(r.status_code, r.text)


class TDx():

    BASE_URL = settings.TDX['URL']
    USERNAME = settings.TDX['USERNAME']
    PASSWORD = settings.TDX['PASSWORD']

    def get_ticket(self, id):
        url = f'{self.BASE_URL}/tickets/{id}'
        return requests.get( url, headers=self.headers )

    def create_ticket(self, payload):
        data = json.dumps(payload)
        url = f'{self.BASE_URL}/31/tickets/'
        return requests.post( url, headers=self.headers, json=payload )

    def get_attributes(self):
        url = f'{self.BASE_URL}/attributes/custom?componentId=9'
        response = requests.get( url, headers=self.headers )
        print(response, response.status_code)
        return json.loads(response.text)

    def get_attribute_by_id(self, id):
        attr_list = self.get_attributes()
        for attr in attr_list:
            if attr['ID'] == id:
                formatted = json.dumps(attr, indent=2)
                print(formatted)

    def get_child_attributes(self, parent_id):
        attr_list = self.get_attributes()
        for attr in attr_list:
            if attr['ParentAttributeID'] == parent_id:
                print(attr['ID'], attr['Name'])

    def get_choices(self, id):
        url = f'{self.BASE_URL}/attributes/{id}/choices'
        return requests.get( url, headers=self.headers )   

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
