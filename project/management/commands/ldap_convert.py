from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from oscauth.models import LDAPGroup, LDAPGroupMember
from django.db import models
from project.integrations import MCommunity
import datetime, csv
from oscauth.utils import get_mc_group

# Throwaway program to convert LDAP id to use GID 

# create table srs_oscauth_ldapgroup_temp as
# select id, name, active, 0 as gid 
# from srs_oscauth_ldapgroup


class GroupTemp(models.Model):
    name = models.TextField()
    active = models.BooleanField()
    gid = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'oscauth_ldapgroup_temp'


class Command(BaseCommand):
    help = 'Convert LDAP tables to use gidNumber as PK'

    def handle(self, *args, **options):
        print(datetime.datetime.now(), 'start')

        mc = MCommunity()

        for group in GroupTemp.objects.all().order_by('id'):

            mc_group = mc.get_group(group.name)

            if mc.conn.entries:
                entry = mc.conn.entries[0]
                group.gid = int(entry.gidNumber.value)
                group.save()
            else:
                print('expired')
