import csv
from pathlib import Path
from django.utils import timezone
from django.db import transaction
from order.models import Server, ServerDisk
from project.models import Choice
from oscauth.models import LDAPGroup


from django.core.management.base import BaseCommand, CommandError

from order.models import ArcInstance

import datetime, json

BYTES_PER_TERABYTE = 1024 ** 4   # Base 2

class Command(BaseCommand):
    help = 'Import CSV from MiServer'

    def handle(self, *args, **options):
        import_servers()


CSV_PATH = Path("/Users/djamison/Downloads/dent_server.csv")


ON_CALL_MAP = {
    "businesshours": Server.BUSINESS_HOURS,
    "24x7": Server.ALL_HOURS,
    "24/7": Server.ALL_HOURS,
}



def get_choice(parent_code, code):
    if not code:
        return None
    return Choice.objects.get(
        #parent_id=94,
        label=code
    )


def parse_disks(text):
    """
    Returns a list of dicts:
    [
      {'name': 'disk0', 'size': 90, 'controller': 0, 'device': 0},
      ...
    ]
    """
    disks = []

    for line in text.splitlines():
        if not line.strip():
            continue

        parts = {}
        for item in line.split(";"):
            key, value = item.split("=", 1)
            parts[key.strip()] = value.strip()

        disks.append({
            "name": parts["name"],
            "size": int(parts["size"]),
            "controller": int(parts["controller"]),
            "device": int(parts["device"]),
        })

    return disks



def create_server_disks(server, disk_text):
    disks = parse_disks(disk_text)

    objs = [
        ServerDisk(
            server=server,
            name=d["name"],
            size=d["size"],
            controller=d["controller"],
            device=d["device"],
        )
        for d in disks
    ]

    ServerDisk.objects.bulk_create(objs)



@transaction.atomic
def import_servers(csv_path=CSV_PATH):
    created = 0
    errors = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for line_no, row in enumerate(reader, start=2):

            owner = LDAPGroup.objects.get(name=row["owner"])
            admin = LDAPGroup.objects.get(name=row["admin_group"])

            try:
                server = Server.objects.create(
                    name=row["name"].strip(),
                    owner=owner,
                    admin_group=admin,
                    os=get_choice("WINDOWS", row["osFull"]),
                    cpu=int(row["cpu"]),
                    ram=int(row["ram"]),
                    shortcode=row["shortcode"],
                    on_call=1,
                    support_email=row["support_email"],
                    support_phone=row["support_phone"],
                    replicated = False,
                    backup = False,
                    billable = False,
                    #patch_time=get_choice("SERVER_PATCH_TIME", row["patch_time"]),
                    #patch_day=get_choice("SERVER_PATCH_DATE", row["patch_day"]),
                    created_date=timezone.now(),
                )
            except Exception as e:
                print('error', e)


            disk_blob = row["disks"]  # CSV column

            create_server_disks(server, disk_blob)

            created += 1
            print( server, created )



    return created, errors
