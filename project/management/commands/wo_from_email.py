from django.core.management.base import BaseCommand

from project.pinnmodels import UmOscPreorderApiV


class Command(BaseCommand):
    help = 'Check pinnacle email box and create an incident in Pinnacle'

    def handle(self, *args, **options):
        # Get emails

        self.create_incident()


    def create_incident(self):

        incident = UmOscPreorderApiV()
        incident.wo_type_category_id = 1            # Incident
        incident.wo_type_code = 'WI'                # Web Incident
        incident.assigned_labor_code = 'GROUP_5'
        incident.comment_text = 'Email body'
        incident.save()