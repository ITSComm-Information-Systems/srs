import csv, json
from django.http import HttpResponse 
from django.db import connections, connection
from project.integrations import MCommunity

def download_csv_from_queryset(queryset, file_name='full_list'):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

    writer = csv.writer(response)

    choice_related = []
    row = []

    if type(queryset[0]) == dict:
        fields = queryset[0].keys()
        for field in queryset[0].keys():
            row.append(field)

        writer.writerow(row)
        for rec in queryset:
            row = []
            for value in rec.values():
                row.append(value)
            writer.writerow(row)

        return response

    fields = queryset.model._meta.fields

    for field in fields:
        row.append(field.name)
        if field.related_model:
            choice_related.append(field.name)

    writer.writerow(row)

    #instance_list = list(self.model.objects.all().select_related(*choice_related))
    for instance in queryset:
        row = []
        for field in fields:
                row.append(getattr(instance,field.name))

        writer.writerow(row)

    return response


def get_or_create_contact(user, dept_id=None):  # Return Pinnacle contact ID for a user, if it does not exist, create one.

    try:
        with connections['pinnacle'].cursor() as cursor:
            resp = cursor.callproc('pinn_custom.um_osc_util_k.um_get_contact_id_p', (user.username, 0, 0))

            if resp[1]:
                return resp[1]
            
            mc_user = MCommunity().get_user(user.username)  # Get user's Phone Number and DeptID

            hr = mc_user.umichHR.value
            pos = hr.find('deptId')
            dept_id = hr[pos+7:pos+13]

            cursor.callproc('pinn_custom.um_osc_util_k.um_add_new_contact_p', [user.username, user.first_name, None, user.last_name, user.email, mc_user.telephoneNumber.value, dept_id])

            resp = cursor.callproc('pinn_custom.um_osc_util_k.um_get_contact_id_p', (user.username, 0, 0))

            if resp[1]:
                return resp[1]
    except:
        print('error getting Pinnacle contact')

def get_query_result(sql, parms=(), json_fields=None):  # Take raw SQL string and return a list of dict

    with connection.cursor() as cursor:
        cursor.execute(sql, parms)
        instances = dictfetchall(cursor, json_fields)

    return instances


def dictfetchall(cursor, json_fields): # Return all rows from a cursor as a dict

    columns = [col[0].lower() for col in cursor.description]

    result_array = []

    for row in cursor.fetchall():

        row_as_dict = dict(zip(columns, row))

        if json_fields != None:
            for field in json_fields:
                row_as_dict[field] = json.loads(row_as_dict[field])

        result_array.append(row_as_dict)

    return result_array