from django.core.management.base import BaseCommand, CommandError
from order.models import Order

class Command(BaseCommand):
    help = 'Resubmit Orders that failed.'

    def handle(self, *args, **options):
        for order in Order.objects.filter(order_reference='Submitting'):
            print(order.id, 'Resubmit')

            order.create_preorder(tries=1)



            