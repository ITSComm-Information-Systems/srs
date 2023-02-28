from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from order.models import Item
from project.integrations import MCommunity, ShortCodesAPI, Openshift
import yaml
from django.conf import settings

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('--shortcode')
        parser.add_argument('--username')
        parser.add_argument('--item')
        parser.add_argument('--os')


    def handle(self, *args, **options):

        if options['os']:


            os = Openshift()
            body = os.get_yaml('backup')
            print(body)
            return

            #with open(f'/Users/djamison/Downloads/{filename}', encoding='mac_roman') as csv_file:
            #    print('x')
            print(settings.BASE_DIR)
            size_yaml = settings.BASE_DIR + '/project/backup.yaml'
            #size_yaml = '/Users/djamison/Downloads/backup.yaml'
            with open(size_yaml, 'r') as f:
                body = yaml.safe_load(f)
            print(body)
            return

        if options['shortcode']:
            sc = ShortCodesAPI()
            print(sc.AUTH_TOKEN)
            r = sc.get_shortcode(options['shortcode'])
            print(r.status_code, r.text)
            return

        if options['username']:
            user = User.objects.get(username=options['username'])
            print(user)

            mc = MCommunity()
            mc.conn.search('ou=Groups,dc=umich,dc=edu', '(cn=SRS Service Entitlement Control)', attributes=["groupMember"])
            print(mc.conn.entries)

            for perm in user.user_permissions.all():
                print(perm, perm.codename)

            print( user.has_perm('oscauth.can_order') )
            print( user.has_perm('can_report') )
            print( user.has_perm('project.can_order') )
            print( user.has_perm('oscauth.can_administer_access') )
            print( user.has_perm('can_administer_access') )
            return

        if options['item']:
            id = options['id']

            print('id', id)
            item = Item.objects.get(id=id)
            #item.route()