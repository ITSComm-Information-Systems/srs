from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.core.management.commands import dumpdata

from order.models import Service, Action, Step, Element

class Command(BaseCommand):
    help = 'Export Action as fixture'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('actions', type=str)

    def handle(self, *args, **options):
        actions=options['actions']
        filename=options['filename']

        action_list = actions.split(',')
        
        service_list = list(Action.objects.filter(id__in=action_list).values_list('service_id', flat=True))
        services = str(service_list).strip('[]')

        step_list = list(Step.objects.filter(action__in=action_list).values_list('id', flat=True))
        steps = str(step_list).strip('[]')

        action_step_list = list(Action.steps.through.objects.filter(action__in=action_list).values_list('id', flat=True))
        action_steps = str(action_step_list).strip('[]')

        element_list = list(Element.objects.filter(step__in=step_list).values_list('id', flat=True))
        elements = str(element_list).strip('[]')

        with open(f'order/fixtures/1{filename}.json', 'w') as f:
            management.call_command('dumpdata', 'order.service',pks=services, stdout=f)

        with open(f'order/fixtures/2{filename}.json', 'w') as f:   
            management.call_command('dumpdata', 'order.action',pks=actions, stdout=f)
        
        with open(f'order/fixtures/3{filename}.json', 'w') as f:
            management.call_command('dumpdata', 'order.step',pks=steps, stdout=f)

        with open(f'order/fixtures/4{filename}.json', 'w') as f:
            management.call_command('dumpdata', 'order.action_steps',pks=action_steps, stdout=f)

        with open(f'order/fixtures/5{filename}.json', 'w') as f:
            management.call_command('dumpdata', 'order.element',pks=elements, stdout=f)

        print(f'Actions {action_list} exported to import run:')
        print('python3 manage.py loaddata order/fixtures/1filename.json --database qa')