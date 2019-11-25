#from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from order.models import Item
from ast import literal_eval


class Command(BaseCommand):
    help = 'One time job to convert reviewSummary to JSON'

    def handle(self, *args, **options):
        print('init')
        item_list = Item.objects.all()

        for item in item_list:
            data = []
            summary = item.data['reviewSummary']

            if isinstance(summary, str):
                print(item.id)
                js = literal_eval(summary)

                for tab in js['tabs']:
                    tabdata = []
                    for title in tab:
                        fields = tab[title]
                        for field in fields:
                            tabdata.append({'label': field, 'value': fields[field]})

                    tab = {'title': title, 'fields': tabdata}
                    data.append(tab)

            item.data['reviewSummary'] = data
            item.save()

        print('end')
