from django.core.management.base import BaseCommand, CommandError

from django.db import models
from project.pinnmodels import UmOscChartcomInitialLoadV
from order.models import Chartcom

class Command(BaseCommand):
    help = 'Load chartcom favorites'

    def handle(self, *args, **options):
        fave_list = UmOscChartcomInitialLoadV.objects.order_by('dept')
        fave_count = UmOscChartcomInitialLoadV.objects.count()
        fave_added_count = 0
        fave_not_added_count = 0

        for row in fave_list:
            try:
                new_record = Chartcom()
                new_record.fund = row.fund  
                new_record.dept = row.deptid
                new_record.program = row.program
                new_record.class_code = row.class_code
                new_record.project_grant = row.project_grant
                new_record.save()
                auth_added_count = auth_added_count + 1
                print("Added Chartcom for Fund: %s  Dept: %s  Program: %s  Class: %s  PG: %s" % (row.fund, row.dept, row.program, row.class_code, row.project_grant))
            except:
                fave_not_added_count = fave_not_added_count + 1
                print("Unable to add Chartcom for Fund: %s  Dept: %s  Program: %s  Class: %s  PG: %s" % (row.fund, row.dept, row.program, row.class_code, row.project_grant))
 
        print('-------------------------------------------')
        print('UmOscChartcomInitialLoadV records read: %s' % fave_count) 
        print('Records added to Chartcom: %s' % fave_added_count) 
        print('Records not added to Chartcom: %s' % fave_not_added_count) 
        print('-------------------------------------------')
 
