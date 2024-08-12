from django.core.management.base import BaseCommand
from project.integrations import TDx
from django.db import models


class TDxTemp(models.Model):
    tdx = models.BigIntegerField(primary_key=True)
    pinnacle = models.CharField(max_length=26, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_TDX_TEMP'


class Command(BaseCommand):
    help = 'TDx read API Data and import into temp table.'

    def handle(self, *args, **options):
        tdx = TDx()

        for rec in TDxTemp.objects.filter(pinnacle__isnull=True):
            print('tdx', rec.tdx)
    
            r = tdx.get_ticket(rec.tdx)

            for attr in r.json().get('Attributes'):
                if attr['ID'] == 2358:
                    pinn_num = attr['Value']
                    print('pinn', pinn_num)
                    rec.pinnacle = pinn_num
                    rec.save()

