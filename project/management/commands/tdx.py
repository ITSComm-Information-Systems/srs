from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import requests, json

class Command(BaseCommand):
    help = 'TDx read API Data'

    def add_arguments(self, parser):
        parser.add_argument('id',type=int)


    def handle(self, *args, **options):
        id = options['id']
        tdx = TDx()
        tdx.get_attribute_by_id(id)
        #tdx.get_child_attributes(id)
        #tdx.get_choices(id)


class TDx():

    BASE_URL = 'https://teamdynamix.umich.edu/SBTDWebApi/api'

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
        response = requests.get( url, headers=self.headers )
        print(response, response.status_code, response.text)     

    def __init__(self):
        print('get token')
        self._get_token()

    def _get_token(self):
        url = self.BASE_URL + '/auth/loginadmin'

        headers = {'Content-Type': 'application/json; charset=utf-8'}

        data = {
            'BEID': 'A6E30356-6BC6-46E5-8E5A-8C2AF9C0AF18',
            'WebServicesKey': '257D64C2-8E4E-4A96-AD94-BEF42C7EC64B'
        }

        data_string = json.dumps(data)
        response = requests.post(url, data=data_string, headers=headers )

        print(response, response.status_code, response.text)

        self.headers = {
            'Authorization': 'Bearer ' + response.text,
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
            }