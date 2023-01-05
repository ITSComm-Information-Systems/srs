from django.core.management.base import BaseCommand
from services.models import BaseImage
import csv

class Command(BaseCommand):
    help = 'Loads data from a CSV file into the base_image table'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to load data from')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        # Open the CSV file and read the data
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)



        # Iterate through the data and create a BaseImage instance for each record
        for record in data:
            gpuBoolean = False
            if record['GPU'] == 'TRUE':
                gpuBoolean = True
                
            image = BaseImage(
                image_name=record['BaseImage'],
                cpu=record['CPU'],
                memory=record['MemoryGb'],
                storage=record['TotalDiskGb'],
                gpu=gpuBoolean
            )
            
            image.save()
        
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
