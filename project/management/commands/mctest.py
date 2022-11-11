from ast import Str
from re import M
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups

from django.contrib.auth.models import User, Group
from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item, Ticket, Server
from oscauth.models import LDAPGroup
from project.integrations import MCommunity

import requests, json
#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('username',type=str)


    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        print(user)

        for perm in user.user_permissions.all():
            print(perm, perm.codename)

        print( user.has_perm('oscauth.can_order') )
        print( user.has_perm('can_report') )
        print( user.has_perm('project.can_order') )
        print( user.has_perm('oscauth.can_administer_access') )
        print( user.has_perm('can_administer_access') )


        return




        mc = MCommunity()

        x = 0

        #for server in Server.objects.distinct('admin_group__name').select_related('admin_group').order_by('admin_group__name'):
        #    print(server.admin_group.name)
        #    mc.add_entitlement(server.admin_group.name)

        mc.conn.search('ou=Groups,dc=umich,dc=edu', '(cn=SRS Service Entitlement Control)', attributes=["groupMember"])
        print(mc.conn.entries)

        return


        id = options['id']

        print('id', id)
        item = Item.objects.get(id=id)

        #ticket_list = Ticket.objects.all()

        #for ticket in ticket_list
        item.route()
        #self.get_ticket()

    def get_ticket(self):

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

        attributes = []
        for id in range(1840, 1880):
            attributes.append({'ID': id, 'Value': id})



        headers = {
            'X-IBM-Client-Id': client_id,
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json' 
            }


        #response = requests.post( base_url + '/um/it/31/tickets', data=data_string, headers=headers )
        response = requests.get( base_url + '/um/it/31/tickets/680842', headers=headers )

        print(response.text)