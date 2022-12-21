from django.core.management.base import BaseCommand
import json

from myapp.models import VirtualDesktop

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        with open(json_file, 'r') as f:
            data = json.load(f)

        for item in data:
            computer = VirtualDesktop(
                shortcode=item['shortcode'],
                pool_name=item['pool_name'],
                gpu=item['gpu'],
                memory=item['memory'],
                cpu=item['cpu'],
                storage=item['storage'],
                individual_cost=item['individual_cost'],
                num_computers=item['num_computers'],
                total_cost=item['total_cost'],
                group=item['group']
            )
            computer.save()

