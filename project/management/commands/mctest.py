from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from order.models import Item
from project.integrations import MCommunity, ShortCodesAPI, Openshift


class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('--shortcode')
        parser.add_argument('--username')
        parser.add_argument('--item')
        parser.add_argument('--osproject')

    def handle(self, *args, **options):

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

        if options['osproject']:
            name = options['osproject']

            os = Openshift()
            os.get_project(name)


