from django.core.management.base import BaseCommand, CommandError

from oscauth.utils import upsert_user
from django.contrib.auth.models import User
from order.models import Order

class Command(BaseCommand):
    help = 'Create Preorder'

    def add_arguments(self, parser):
        parser.add_argument('order',type=int)

    def handle(self, *args, **options):
        order = Order.objects.get(id=options['order'])
        order.create_preorder()
        print('Preorder',order.order_reference)





            