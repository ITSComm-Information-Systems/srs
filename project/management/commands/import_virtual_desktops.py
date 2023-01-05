from django.core.management.base import BaseCommand
from services.models import VirtualPool
import json

class Command(BaseCommand):
    # Add command-line arguments for the command
    def add_arguments(self, parser):
        # Add an argument for the path to the JSON file
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    # Handle the command
    def handle(self, *args, **kwargs):
        # Get the path to the JSON file from the command-line arguments
        json_file = kwargs['json_file']

        # Open the JSON file and load the data
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Iterate over the items in the data
        for item in data:
            # Create a VirtualPool instance with the item data
            computer = VirtualPool(
                shortcode=item['shortcode'],
                pool_name=item['pool_name'],
                individual_cost=item['individual_cost'],
                num_computers=item['num_computers'],
                total_cost=item['total_cost'],
                admin_group=item['group']
            )
            # Save the instance to the database
            computer.save()
