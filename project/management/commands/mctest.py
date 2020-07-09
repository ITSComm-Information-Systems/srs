from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import get_mc_group, McGroup
from order.models import BackupDomain, BackupNode, Item
from oscauth.models import LDAPGroup

#import datetime, csv

class Command(BaseCommand):
    help = 'Add Backup Domain'

    def add_arguments(self, parser):
        parser.add_argument('id',type=int)


    def handle(self, *args, **options):

        id = options['id']
        item = Item.objects.get(id=id)

        bd = BackupDomain.objects.get(id=item.data.get('instance_id'))
        print(bd)

        #node_set = set()
        #nodes = BackupNode.objects.filter(backup_domain=bd)

        #for node in nodes:
        #    node_set.add(node.name)
            

        #print(node_set)

        time_list = item.data['backupTime']
        for num, node in enumerate(item.data['nodeNames']):
            if node != '':
                time = time_list[num]
                print('request', node, time_list[num])
                new_node = BackupNode.objects.get_or_create(backup_domain=bd, name=node, defaults={'time': time})
                new_time = new_node[0].time
                if new_time != time:
                    new_node[0].time = time
                    new_node[0].save()

        ex = BackupNode.objects.filter(backup_domain=bd).exclude(name__in=item.data['nodeNames']).delete()
        



        
    